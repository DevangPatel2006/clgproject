import axios from 'axios';
import fs from 'fs'; // Use standard fs module, createWriteStream is synchronous setup
import { promises as fsPromises } from 'fs'; // Use promises for async operations like access, mkdir, unlink
import path from 'path';
import AppError from '../../utils/AppError.js';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { PYTHON_API_BASE_URL } from '../../config/index.js'; // Import the base URL

// Helper to get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Define the correct upload folder path relative to the *project root*
// process.cwd() gives the directory where the Node process was started
const UPLOAD_FOLDER = path.resolve(process.cwd(), 'uploads');
const MAPPED_FILE_PATH = path.join(UPLOAD_FOLDER, 'mapped_data.xlsx'); // Consistent naming

// Function to ensure the uploads directory exists
const ensureUploadsFolder = async () => {
    try {
        await fsPromises.access(UPLOAD_FOLDER);
    } catch (error) {
        // If directory doesn't exist, create it
        if (error.code === 'ENOENT') {
            await fsPromises.mkdir(UPLOAD_FOLDER, { recursive: true });
            console.log(`Created uploads directory at: ${UPLOAD_FOLDER}`);
        } else {
            // Re-throw other errors
            throw error;
        }
    }
};

/**
 * Calls the Python server to execute the data processing pipeline.
 */
export const processData = async () => {
  // Use the environment variable for the URL
  const RUN_PIPELINE_URL = `${PYTHON_API_BASE_URL}/run_pipeline`;
  try {
    console.log(`Sending request to Python server at: ${RUN_PIPELINE_URL}`);
    const response = await axios.post(RUN_PIPELINE_URL);
    console.log('Python server responded:', response.data);

    if (response.data && response.data.status === 'success') {
      return `Pipeline executed successfully by Python server. ${response.data.message}`;
    } else {
      // Handle potential errors reported by the Python script
      const errorMessage = response.data?.message || 'An unknown error occurred in the Python pipeline.';
      throw new AppError(errorMessage, response.status || 500);
    }

  } catch (error) {
    console.error('Error triggering the Python pipeline:', error.message);

    // If it's already an AppError, re-throw it
    if (error instanceof AppError) {
      throw error;
    }

    if (error.response) {
      // Error came from the Python server's response
      const pythonErrorMessage = error.response.data?.message || 'Python service returned an error.';
      // Log the detailed Python error if available
      console.error('Python Error Details:', error.response.data);
      throw new AppError(pythonErrorMessage, error.response.status);
    } else if (error.request) {
      // Request was made but no response received
      throw new AppError('The Python processing service is unavailable or did not respond.', 503); // 503 Service Unavailable
    } else {
      // Something happened in setting up the request
      throw new AppError('Failed to run pipeline. Could not communicate with the Python service.', 500);
    }
  }
};

/**
 * Fetches the mapped file from the Python server and saves it locally
 * in the designated UPLOAD_FOLDER.
 */
export const getMappedFile = async () => {
    // Use the environment variable for the URL and correct endpoint
    const DOWNLOAD_URL = `${PYTHON_API_BASE_URL}/download_mapped`;
    try {
        console.log(`Requesting mapped file from: ${DOWNLOAD_URL}`);
        // Ensure the target directory exists before attempting to download/save
        await ensureUploadsFolder();

        // Request the file stream from the Python server
        const response = await axios.get(DOWNLOAD_URL, {
            responseType: 'stream',
        });

        // Create a write stream to save the file to the correct path
        const writer = fs.createWriteStream(MAPPED_FILE_PATH);

        // Pipe the downloaded data into the write stream
        response.data.pipe(writer);

        // Return a promise that resolves when the file is finished writing or rejects on error
        return new Promise((resolve, reject) => {
            writer.on('finish', () => {
                console.log(`Mapped file saved successfully to: ${MAPPED_FILE_PATH}`);
                // Resolve with the path and the desired filename for download response
                resolve({ filePath: MAPPED_FILE_PATH, fileName: 'mapped_data.xlsx' });
            });
            writer.on('error', (err) => {
                console.error('Error writing downloaded file:', err);
                // Attempt to clean up potentially incomplete/corrupted file
                fsPromises.unlink(MAPPED_FILE_PATH).catch(unlinkErr => console.error('Error cleaning up failed download:', unlinkErr));
                reject(new AppError('Failed to save the downloaded mapped file.', 500));
            });
             // Also handle errors originating from the download stream itself
             response.data.on('error', (err) => {
                 console.error('Error in download stream:', err);
                 reject(new AppError('Error occurred during file download stream.', 500));
            });
        });

    } catch (error) {
        console.error('Error communicating with Python service for download:', error.message);

        // Check if it's an error response from Python
        if (error.response) {
            // Specifically handle the 404 Not Found case
            if (error.response.status === 404) {
                 throw new AppError('Mapped file not found on Python server. Please run the pipeline first.', 404);
            }
            // Handle other Python server errors
            const pythonErrorMessage = error.response.data?.message || 'Python service returned an error during download.';
            console.error('Python Download Error Details:', error.response.data);
            throw new AppError(pythonErrorMessage, error.response.status);
        } else if (error.request) {
            // No response from Python server
            throw new AppError('The Python processing service is unavailable or did not respond for download.', 503);
        } else {
            // Other errors (e.g., network issues, DNS resolution)
            throw new AppError('Failed to initiate download from Python service.', 502); // 502 Bad Gateway often suitable here
        }
    }
};