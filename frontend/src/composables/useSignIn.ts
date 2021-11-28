import { NForm, useMessage } from "naive-ui";
import { reactive, ref } from "vue";
import { axiosConfigFactory, AuthApiFactory } from "@/api/index";


export default () => {
    const message = useMessage();
    const API = AuthApiFactory(undefined, axiosConfigFactory().basePath);

    const formRef = ref<null | typeof NForm>(null)
    const formVals = reactive({ email: "" as string, password: "" as string })
    const formRules = {
        email: {
            required: true,
            trigger: 'blur',
            message: 'Please enter your email address'
        },
        password: {
            required: true,
            trigger: 'blur',
            message: 'Please enter your password'
        }
    };
    const onSignIn = (successCallback: Function) => {
        return () => {
            // Frontend validation first.
            if (!formRef.value) {
                console.error("Sign in formref not mounted.")
                return;
            }
            formRef.value.validate((errors: any) => {
                if (errors) {
                    message.error("Invalid sign in.")
                }
            });
        

            if (formVals.email && formVals.password) {
                API.loginAuthTokenPost(formVals.email, formVals.password).then(response => {
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
        formRef,
        formRules,
        formVals,
        onSignIn
    };
};