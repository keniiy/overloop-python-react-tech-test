export const collectDetailMessages = (detail) => {
  if (!detail) {
    return [];
  }

  if (Array.isArray(detail)) {
    return detail.flatMap((item) => collectDetailMessages(item));
  }

  if (typeof detail === 'string') {
    return [detail];
  }

  if (typeof detail === 'object') {
    const messages = [];

    if (detail.msg) {
      messages.push(detail.msg);
    }

    if (detail.message) {
      messages.push(detail.message);
    }

    if (detail.details) {
      messages.push(...collectDetailMessages(detail.details));
    }

    return messages;
  }

  return [];
};

export const formatApiError = (error, fallbackMessage = 'Something went wrong') => {
  if (!error) {
    return fallbackMessage;
  }

  const responseData = error.response?.data;

  if (!responseData) {
    return error.message || fallbackMessage;
  }

  const messages = [];

  if (responseData.error) {
    messages.push(responseData.error);
  }

  const detailMessages = collectDetailMessages(responseData.details);
  if (detailMessages.length > 0) {
    messages.push(...detailMessages);
  }

  const joined = messages.filter(Boolean).join(' | ');
  return joined || fallbackMessage;
};
