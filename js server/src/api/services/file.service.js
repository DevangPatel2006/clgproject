import path from 'path';
import { promises as fs } from 'fs';
import AppError from '../../utils/AppError.js';
import { resetPythonFiles } from './pipeline.service.js'; // Import the reset function

const UPLOAD_FOLDER = path.join(process.cwd(), 'uploads');
const MAPPED_FILE_PATH = path.join(UPLOAD_FOLDER, 'mapped_data.xlsx');
const TEMP_FOLDER_NAME = 'temp'; // Define the temp folder name

const ensureUploadsFolder = async () => {
    try {
        await fs.access(UPLOAD_FOLDER);
    } catch {
        await fs.mkdir(UPLOAD_FOLDER, { recursive: true });
    }
};

export const handleFileUpload = async (file, requestPath) => {
    if (!file) {
        throw new AppError('No file uploaded.', 400);
    }
    await ensureUploadsFolder();
    const filename = requestPath.includes('upload_raw') ? 'raw_data.xlsx' : 'master_file.xlsx';
    const finalPath = path.join(UPLOAD_FOLDER, filename);

    // Make sure the temp directory exists before trying to rename from it
    const tempDir = path.dirname(file.path);
    try {
        await fs.access(tempDir);
    } catch {
        await fs.mkdir(tempDir, { recursive: true });
    }

    await fs.rename(file.path, finalPath);
    return `${filename} uploaded successfully.`;
};

export const getListofFiles = async () => {
    await ensureUploadsFolder();
    const files = await fs.readdir(UPLOAD_FOLDER);
    return files;
};

export const getFilePath = async (filename) => {
    const filePath = path.join(UPLOAD_FOLDER, filename);
    // Prevent trying to access files within the temp directory via this route
    if (filename === TEMP_FOLDER_NAME || filename.startsWith(TEMP_FOLDER_NAME + path.sep)) {
         throw new AppError('Access to temporary files is restricted.', 403);
    }
    try {
        await fs.access(filePath);
        return { filePath, fileName: filename };
    } catch {
        throw new AppError('File not found.', 404);
    }
};

export const getMappedFilePath = async () => {
    try {
        await fs.access(MAPPED_FILE_PATH);
        return { filePath: MAPPED_FILE_PATH, fileName: 'mapped_data.xlsx' };
    } catch {
        throw new AppError('Mapped file not found. Please run the pipeline first.', 404);
    }
};

/**
 * Deletes all files and subdirectories within the UPLOAD_FOLDER,
 * except for the TEMP_FOLDER_NAME directory itself.
 * Also triggers Python server reset to delete mapped files there.
 */
export const resetUploads = async () => {
    await ensureUploadsFolder();
    console.log(`Resetting contents of: ${UPLOAD_FOLDER}, excluding '${TEMP_FOLDER_NAME}'`);

    try {
        // Step 1: Reset Python server files first
        console.log('Step 1: Resetting Python server files...');
        try {
            await resetPythonFiles();
            console.log('✅ Python server files deleted successfully');
        } catch (pythonError) {
            console.error('⚠️ Warning: Failed to reset Python files:', pythonError.message);
            // Continue with JS reset even if Python reset fails (Python might be offline)
        }

        // Step 2: Reset JS server files
        console.log('Step 2: Resetting JS server files...');
        const entries = await fs.readdir(UPLOAD_FOLDER, { withFileTypes: true });

        // Create a list of promises for deletion
        const deletionPromises = entries.map(entry => {
            const entryPath = path.join(UPLOAD_FOLDER, entry.name);
            // Skip the temp folder
            if (entry.name === TEMP_FOLDER_NAME) {
                console.log(`Skipping deletion of: ${entryPath}`);
                return Promise.resolve(); // Resolve immediately for the temp folder
            }
            // Delete other files or directories
            console.log(`Attempting to delete: ${entryPath}`);
            return fs.rm(entryPath, { recursive: true, force: true });
        });

        // Wait for all deletions to complete
        await Promise.all(deletionPromises);

        console.log(`✅ Contents of ${UPLOAD_FOLDER} (excluding ${TEMP_FOLDER_NAME}) deleted.`);
        console.log('✅ Reset completed for both JS and Python servers.');
        return 'All uploaded files have been deleted from both servers.';

    } catch (error) {
        console.error(`❌ Error during reset operation in ${UPLOAD_FOLDER}:`, error);
        
        if (error.code === 'ENOENT') {
             console.warn(`Upload folder (${UPLOAD_FOLDER}) might not have existed during reset.`);
             await ensureUploadsFolder();
             return 'Upload folder was missing or empty; ensured it exists now.';
        }
        // Re-throw other unexpected errors
        throw new AppError('Failed to reset uploaded files.', 500);
    }
};