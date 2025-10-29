import express from 'express';
import cors from 'cors';
import { PORT } from './src/config/index.js';
import AppError from './src/utils/AppError.js';
import { errorHandler } from './src/api/middlewares/errorHandler.js';
import apiRouter from './src/api/routes/index.js';

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use('/api', apiRouter);

app.get('/', (req, res) => {
    res.status(200).json({ status: 'OK', message: 'Server is running' });
});

// Corrected 404 Handler
app.use((req, res, next) => {
    next(new AppError(`Can't find ${req.originalUrl} on this server!`, 404));
});

app.use(errorHandler);

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});