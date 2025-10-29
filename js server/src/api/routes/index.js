import { Router } from 'express';
import fileRouter from './file.routes.js';
import pipelineRouter from './pipeline.routes.js';

const router = Router();

router.use('/files', fileRouter);
router.use('/pipeline', pipelineRouter);

export default router;