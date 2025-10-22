import api from '../utils/api';

export const listRegions = async () => {
    const response = await api.get('regions');
    const payload = response.data;

    if (Array.isArray(payload)) {
        return payload;
    }

    if (payload?.data && Array.isArray(payload.data)) {
        return payload.data;
    }

    return [];
};
