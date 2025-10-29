import { Router } from 'express';
import {
    uploadFile,
    listFiles,
    downloadFile,
    downloadMappedFile,
    reset,
} from '../Controllers/file.controller.js';
import upload from '../middlewares/upload.js';

const router = Router();

router.post('/upload_raw', upload.single('raw_data'), uploadFile);
router.post('/upload_master', upload.single('master_file'), uploadFile);
router.get('/list_files', listFiles);
router.get('/download/:filename', downloadFile);
router.get('/download_mapped', downloadMappedFile);
router.post('/reset', reset);

export default router;