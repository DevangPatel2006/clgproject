import axios from 'axios';
import fs from 'fs';
import { promises as fsPromises } from 'fs';
import path from 'path';
import FormData from 'form-data'; // Make sure you have this import
import AppError from '../../utils/AppError.js';
import { PYTHON_API_BASE_URL } from '../../config/index.js';

const UPLOAD_FOLDER = path.resolve(process.cwd(), 'uploads');
const MAPPED_FILE_PATH = path.join(UPLOAD_FOLDER, 'mapped_data.xlsx');
const RAW_DATA_PATH = path.join(UPLOAD_FOLDER, 'raw_data.xlsx');
const MASTER_FILE_PATH = path.join(UPLOAD_FOLDER, 'master_file.xlsx'); // Define path to master file

/**
 * Helper function to upload a file to the Python server
 */
const uploadFileToPython = async (filePath, fieldName, endpoint) => {
    try {
        // Check if file exists
        await fsPromises.access(filePath);
        
        // Create form data
        const form = new FormData();
        form.append(fieldName, fs.createReadStream(filePath));
        
        const uploadUrl = `${PYTHON_API_BASE_URL}${endpoint}`;
        console.log(`Uploading file (${fieldName}) to Python server: ${uploadUrl}`);
        
        // Upload to Python server
        const response = await axios.post(uploadUrl, form, {
            headers: {
                ...form.getHeaders(),
            },
            maxContentLength: Infinity,
            maxBodyLength: Infinity,
        });
        
        console.log(`File (${fieldName}) uploaded successfully to Python server:`, response.data);
        return response.data;
        
    } catch (error) {
        console.error(`Error uploading file (${fieldName}) to Python server:`, error.message);
        
        if (error.code === 'ENOENT') {
            throw new AppError(`Required file not found on JS server: ${path.basename(filePath)}`, 404);
        }
        
        if (error.response) {
            const pythonError = error.response.data?.message || 'Python server returned an error during file upload';
            throw new AppError(pythonError, error.response.status);
        } else if (error.request) {
            throw new AppError('Python processing service is unavailable (file upload)', 503);
        } else {
            throw new AppError('Failed to upload file to Python service', 500);
        }
    }
};


/**
 * Calls the Python server to execute the data processing pipeline.
 */
export const processData = async () => {
  const RUN_PIPELINE_URL = `${PYTHON_API_BASE_URL}/run_pipeline`;
  try {
    
    // Step 1: Delete any old mapped file
    console.log('Step 1: Deleting old mapped file (if it exists)...');
    try {
        await fsPromises.unlink(MAPPED_FILE_PATH);
        console.log('Old mapped_data.xlsx deleted.');
    } catch (error) {
        if (error.code === 'ENOENT') {
            console.log('No old mapped file to delete.'); // This is fine
        } else {
            console.warn(`Warning: Could not delete old mapped file: ${error.message}`);
        }
    }

    // Step 2: Upload raw data file to Python server
    console.log('Step 2: Uploading raw data file...');
    // Note: Python's field name is 'raw_data' and endpoint is '/upload_raw'
    await uploadFileToPython(RAW_DATA_PATH, 'raw_data', '/upload_raw');
    
    // Step 3: Upload master file to Python server
    console.log('Step 3: Uploading master file...');
    // Note: Python's field name is 'master_file' and endpoint is '/upload_master'
    await uploadFileToPython(MASTER_FILE_PATH, 'master_file', '/upload_master');

    // Step 4: Trigger pipeline execution
    console.log('Step 4: Triggering pipeline execution...');
    const response = await axios.post(RUN_PIPELINE_URL);
    console.log('Python server responded:', response.data);

    if (response.data && response.data.status === 'success') {
      return `Pipeline executed successfully by Python server. ${response.data.message}`;
    } else {
      const errorMessage = response.data?.message || 'An unknown error occurred in the Python pipeline.';
      throw new AppError(errorMessage, response.status || 500);
    }

  } catch (error) {
    console.error('Error triggering the Python pipeline:', error.message);
    if (error instanceof AppError) {
      throw error;
    }
    if (error.response) {
      const pythonErrorMessage = error.response.data?.message || 'Python service returned an error.';
      console.error('Python Error Details:', error.response.data);
      throw new AppError(pythonErrorMessage, error.response.status);
    } else if (error.request) {
      throw new AppError('The Python processing service is unavailable or did not respond.', 503);
    } else {
      throw new AppError('Failed to run pipeline. Could not communicate with the Python service.', 500);
    }
  }
};

/**
 * Fetches the mapped file from the Python server and saves it locally
 */
export const getMappedFile = async () => {
    const DOWNLOAD_URL = `${PYTHON_API_BASE_URL}/download_mapped`;
    try {
        console.log(`Requesting mapped file from: ${DOWNLOAD_URL}`);
        
        try {
            await fsPromises.access(UPLOAD_FOLDER);
        } catch {
            await fsPromises.mkdir(UPLOAD_FOLDER, { recursive: true });
        }

        const response = await axios.get(DOWNLOAD_URL, {
            responseType: 'stream',
        });

        const writer = fs.createWriteStream(MAPPED_FILE_PATH);
        response.data.pipe(writer);

        return new Promise((resolve, reject) => {
            writer.on('finish', () => {
                console.log(`Mapped file saved successfully to: ${MAPPED_FILE_PATH}`);
                resolve({ filePath: MAPPED_FILE_PATH, fileName: 'mapped_data.xlsx' });
            });
            writer.on('error', (err) => {
                console.error('Error writing downloaded file:', err);
                fsPromises.unlink(MAPPED_FILE_PATH).catch(unlinkErr => console.error('Error cleaning up failed download:', unlinkErr));
                reject(new AppError('Failed to save the downloaded mapped file.', 500));
            });
             response.data.on('error', (err) => {
                 console.error('Error in download stream:', err);
                 reject(new AppError('Error occurred during file download stream.', 500));
            });
        });

    } catch (error) {
        console.error('Error communicating with Python service for download:', error.message);
        if (error.response) {
            if (error.response.status === 404) {
                 throw new AppError('Mapped file not found on Python server. Please run the pipeline first.', 404);
            }
            const pythonErrorMessage = error.response.data?.message || 'Python service returned an error during download.';
            console.error('Python Download Error Details:', error.response.data);
            throw new AppError(pythonErrorMessage, error.response.status);
        } else if (error.request) {
            throw new AppError('The Python processing service is unavailable or did not respond for download.', 503);
        } else {
            throw new AppError('Failed to initiate download from Python service.', 502);
        }
    }
};

/**
 * Calls the Python server to delete its generated/uploaded files.
 */
export const resetPythonFiles = async () => {
    const resetUrl = `${PYTHON_API_BASE_URL}/reset`;
    
    try {
        console.log(`Requesting file reset from: ${resetUrl}`);
        const response = await axios.post(resetUrl);
        console.log('Python reset response:', response.data);
        
        if (response.data && response.data.status === 'success') {
            return response.data.message;
        } else {
            const errorMessage = response.data?.message || 'An unknown error occurred in the Python reset.';
            throw new AppError(errorMessage, response.status || 500);
        }
        
    } catch (error) {
        console.error('Error resetting Python files:', error.message);
        if (error instanceof AppError) {
            throw error;
        }
        if (error.response) {
            const pythonErrorMessage = error.response.data?.message || 'Python service returned an error during reset.';
            console.error('Python Reset Error Details:', error.response.data);
            throw new AppError(pythonErrorMessage, error.response.status);
        } else if (error.request) {
            throw new AppError('The Python processing service is unavailable or did not respond for reset.', 503);
        } else {
            throw new AppError('Failed to initiate reset on Python service.', 502);
        }
    }
};