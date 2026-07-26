import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const evaluateSingleLog = async (logData) => {
    const response = await axios.post(`${API_BASE_URL}/predict/single`, logData);
    return response.data;
};

export const evaluateSequenceLogs = async (sequenceData) => {
    const response = await axios.post(`${API_BASE_URL}/predict/sequence`, sequenceData);
    return response.data;
};