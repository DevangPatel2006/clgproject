import * as pipelineService from '../services/pipeline.service.js';
import AppError from '../../utils/AppError.js';
import { processData, getMappedFile } from '../services/pipeline.service.js';
export const runPipelineController = async (req, res, next) => {
    try {
        const result = await pipelineService.processData();
        res.status(200).json({
            status: 'success',
            message: result,
        });
    } catch (error) {
        next(error || new AppError('An unexpected error occurred in the pipeline.', 500));
    }
};
export const downloadMappedFileController = async (req, res, next) => {
  try {
    // This service will download the file from Python and give us its temporary path
    const { filePath, fileName } = await getMappedFile();

    // Send the file to the user
    res.download(filePath, fileName, (err) => {
      if (err) {
        // Let the error handler manage any issues
        throw err;
      }
    });
  } catch (error) {
    next(error);
  }
};