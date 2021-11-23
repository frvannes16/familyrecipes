import { useMessage } from "naive-ui";
import { reactive } from "vue";
import { axiosConfigFactory, AuthApiFactory } from "@/api/index";


export default () => {
    const message = useMessage();
    const API = AuthApiFactory(undefined, axiosConfigFactory().basePath);


    const signUp = reactive({ email: "" as string, password: "" as string, confirmPassword: "" as string });

    const onSignUp = (successCallback: Function) => {
        return () => {
            // Verify that confirmed password matches password
            if (signUp.password !== signUp.confirmPassword) {
                message.error("Password and Confirm Password do not match.");
                return;
            }
            // create a new user.
            const createUserResponse = API.createUserAuthUsersPost({
                email: signUp.email,
                password: signUp.password,
            });
            createUserResponse.then(response => {
                if (response?.status == 200 && response?.data) {
                    API.loginAuthTokenPost(response.data.email, signUp.password)
                        .then(response => {
                            if (response.status == 200 && response.data.access_token) {
                                successCallback();
                            }
                        });
                }
            }).catch(error => {
                if (error.response.data?.detail) {
                    message.error(error.response.data.detail);
                } else {
                    message.error(error.response.data);
                }
            })
        }
    };

    return {
        signUp,
        onSignUp
    };
};