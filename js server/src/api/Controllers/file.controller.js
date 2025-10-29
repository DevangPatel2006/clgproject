import * as fileService from '../services/file.service.js';
import AppError from '../../utils/AppError.js';

const handleRequest = (handler) => async (req, res, next) => {
    try {
        await handler(req, res, next);
    } catch (error) {
        next(error || new AppError('An unexpected error occurred.', 500));
    }
};

export const uploadFile = handleRequest(async (req, res) => {
    const message = await fileService.handleFileUpload(req.file, req.path);
    res.status(200).json({ status: 'success', message });
});

export const listFiles = handleRequest(async (req, res) => {
    const files = await fileService.getListofFiles();
    res.status(200).json({ status: 'success', files });
});

export const downloadFile = handleRequest(async (req, res) => {
    const { filePath, fileName } = await fileService.getFilePath(req.params.filename);
    res.download(filePath, fileName);
});

export const downloadMappedFile = handleRequest(async (req, res) => {
    const { filePath, fileName } = await fileService.getMappedFilePath();
    res.download(filePath, fileName);
});

export const reset = handleRequest(async (req, res) => {
    const message = await fileService.resetUploads();
    res.status(200).json({ status: 'success', message });
});