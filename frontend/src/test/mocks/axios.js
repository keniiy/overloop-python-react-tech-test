const methods = ['get', 'post', 'put', 'delete', 'patch'];

const buildMockInstance = () => {
  const instance = {
    interceptors: {
      request: { use: jest.fn(), eject: jest.fn() },
      response: { use: jest.fn(), eject: jest.fn() },
    },
  };

  methods.forEach((method) => {
    instance[method] = jest.fn();
  });

  return instance;
};

const axiosMock = {};
const mockInstance = buildMockInstance();

axiosMock.create = jest.fn(() => mockInstance);
methods.forEach((method) => {
  axiosMock[method] = jest.fn((...args) => mockInstance[method](...args));
});

axiosMock.__reset = () => {
  axiosMock.create.mockReset();
  axiosMock.create.mockImplementation(() => mockInstance);
  methods.forEach((method) => {
    axiosMock[method].mockReset();
    mockInstance[method].mockReset();
  });
  mockInstance.interceptors.request.use.mockReset();
  mockInstance.interceptors.request.eject.mockReset();
  mockInstance.interceptors.response.use.mockReset();
  mockInstance.interceptors.response.eject.mockReset();
};

axiosMock.__getMockInstance = () => mockInstance;

export default axiosMock;
