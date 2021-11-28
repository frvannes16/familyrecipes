import { useMessage, NForm } from "naive-ui";
import { reactive, ref } from "vue";
import { axiosConfigFactory, AuthApiFactory } from "@/api/index";


export default () => {
    const message = useMessage();
    const API = AuthApiFactory(undefined, axiosConfigFactory().basePath);

    const snakeToSpaceCase = (str: string) => {
        return str.replace(/_([A-Za-z])/g, " $1");
    }

    const formRef = ref<null | typeof NForm>(null);
    const formVals = reactive({
        first_name: "" as string,
        last_name: "" as string,
        email: "" as string,
        password: "" as string,
        confirmPassword: "" as string
    });

    const formRules = ref(Object.keys(formVals).reduce((obj, key: string) => {
        const addition = {
            [key]: {
                required: true,
                message: `Please input ${snakeToSpaceCase(key).toLowerCase()}. It is required`,
                trigger: ['blur']
            }
        };
        return { ...obj, ...addition };
    }, {}));



    const onSignUp = (successCallback: Function) => {
        return () => { 
            if (!formRef?.value) {
                console.error("SignUp formRef not used.");
                return
            }
            formRef.value.validate((errors: any) => {
                if (errors) {
                    message.error("SignUp Form Invalid");
                }
            });
            // Verify that confirmed password matches password
            if (formVals.password !== formVals.confirmPassword) {
                message.error("Password and Confirm Password do not match.");
                return;
            }
            // create a new user.
            const createUserResponse = API.createUserAuthUsersPost({
                email: formVals.email,
                password: formVals.password,
                first_name: formVals.first_name,
                last_name: formVals.last_name,
            });
            createUserResponse.then(response => {
                if (response?.status == 200 && response?.data) {
                    API.loginAuthTokenPost(response.data.email, formVals.password)
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
        formRef,
        formRules,
        formVals,
        onSignUp
    };
};