import { Router } from 'express';
// 1. Import the new controller function
import { runPipelineController, downloadMappedFileController } from '../Controllers/pipeline.controller.js';

const router = Router();

router.post('/run_pipeline', runPipelineController);

// 2. Add the new GET route for downloading the file
router.get('/download_mapped', downloadMappedFileController);

export default router;