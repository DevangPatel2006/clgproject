import multer from 'multer';
import fs from 'fs';
import path from 'path';

const uploadDir = 'uploads/temp';

// Create the destination directory if it doesn't exist
fs.mkdirSync(path.resolve(uploadDir), { recursive: true });

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    // Using a unique name to prevent file overwrites
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ storage: storage });
export default upload;