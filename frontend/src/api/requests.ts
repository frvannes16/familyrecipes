

const axiosConfigFactory = () => {
    return {
        basePath: 'https://localhost:8000',  // TODO: Productionize. Everything will be static and same origin.
        timeout: 1000,
    }
}


export default axiosConfigFactory;