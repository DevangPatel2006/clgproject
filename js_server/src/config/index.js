import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

// Load environment variables from .env file located in the parent directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
dotenv.config({ path: path.resolve(__dirname, '..', '..', '.env') }); // Go up two levels to find .env

export const PORT = process.env.PORT || 8000;
export const NODE_ENV = process.env.NODE_ENV || 'development';
export const PYTHON_API_BASE_URL = process.env.PYTHON_API_BASE_URL || 'http://localhost:5000'; // Default fallback

// Add other environment variables here as needed
// Example: export const DATABASE_URL = process.env.DATABASE_URL;