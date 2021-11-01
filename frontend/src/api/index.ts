import axios from "axios";
import axiosConfigFactory from "./requests";

export { axiosConfigFactory };
export * from "../../gen/api/index";
axios.defaults.withCredentials = true;