

const axiosConfigFactory = () => {
    return {
        basePath: 'http://localhost:8000',  // TODO: Productionize. Everything will be static and same origin.
        timeout: 1000
    }
}


export default axiosConfigFactory;