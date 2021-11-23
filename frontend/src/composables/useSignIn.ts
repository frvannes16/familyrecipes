import { useMessage } from "naive-ui";
import { reactive } from "vue";
import { axiosConfigFactory, AuthApiFactory } from "@/api/index";


export default () => {
    const message = useMessage();
    const API = AuthApiFactory(undefined, axiosConfigFactory().basePath);


    const signIn = reactive({ email: "" as string, password: "" as string })
    const onSignIn = (successCallback: Function) => {
        return () => {
            if (signIn.email && signIn.password) {
                API.loginAuthTokenPost(signIn.email, signIn.password).then(response => {
                    if (response?.status == 200 && response.data.access_token) {
                        successCallback();
                    }
                }).catch(error => {
                    if (error.response.data?.detail) {
                        message.error(error.response.data.detail);
                    } else {
                        message.error(error.response.data);
                    }
                });
            }
        }
    }

    return {
        signIn,
        onSignIn
    };
};