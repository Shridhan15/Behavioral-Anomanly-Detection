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

export const fetchDatasetStats = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/stats/distribution`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch dataset stats: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error("API Error (fetchDatasetStats):", error);
        throw error;
    }
};