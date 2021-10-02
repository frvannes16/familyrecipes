<template>
    <div class="container">
        <n-card>
            <n-tabs default-value="signin" size="large">
                <n-tab-pane name="signin" tab="Sign in">
                    <n-form>
                        <n-form-item-row>
                            <n-input v-model:value="signin.email" placeholder="Email" />
                        </n-form-item-row>
                        <n-form-item-row>
                            <n-input
                                v-model:value="signin.password"
                                type="password"
                                show-password-on="mousedown"
                                placeholder="Password"
                            />
                        </n-form-item-row>
                    </n-form>
                    <n-button type="primary" block @click="onSignIn">Sign In</n-button>
                </n-tab-pane>
                <n-tab-pane name="signup" tab="Sign Up">
                    <n-form>
                        <n-form-item-row>
                            <n-input v-model:value="signup.email" placeholder="Email" />
                        </n-form-item-row>
                        <n-form-item-row>
                            <n-input
                                v-model:value="signup.password"
                                type="password"
                                show-password-on="mousedown"
                                :min-length="MIN_PASSWORD_LENGTH"
                                placeholder="Password"
                            />
                        </n-form-item-row>
                        <n-form-item-row>
                            <n-input
                                v-model:value="signup.confirmPassword"
                                type="password"
                                show-password-on="mousedown"
                                :min-length="MIN_PASSWORD_LENGTH"
                                placeholder="Confirm password"
                            />
                        </n-form-item-row>
                    </n-form>
                    <n-button type="primary" block @click="onSignUp">Sign Up</n-button>
                </n-tab-pane>
            </n-tabs>
        </n-card>
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { NButton, NInput, NForm, NFormItem, NTabs, NTabPane, NFormItemRow, NCard } from 'naive-ui';
import api from "../api/requests";


export default defineComponent({
    components: { NButton, NInput, NForm, NFormItem, NTabs, NTabPane, NFormItemRow, NCard },
    data() {
        return {
            signin: {
                email: "",
                password: ""
            },
            signup: {
                email: "",
                password: "",
                confirmPassword: ""

            },
            MIN_PASSWORD_LENGTH: 12
        }
    },
    methods: {
        onSignUp() {
            // create a new user.
            console.log("on Sign Up ", this.signup)
            const responsePromise = api.post("/auth/users/", {
                email: this.signup.email,
                password: this.signup.password
            });
            responsePromise.then(response => {
                if (response?.status == 200 && response?.data) {
                    console.log("user succesfully created. Signing in");
                    this.signIn(this.signup.email, this.signup.password).then(response => {
                        if (response?.status == 200 && response?.data?.access_token) {
                            console.log(response.data.access_token);
                        }
                    });
                } else {
                    console.log(response);
                }
            }).catch(error => {
                console.error(error);
            })
        },
        onSignIn() {
            if (this.signin.email && this.signin.password) {
                this.signIn(this.signin.email, this.signin.password).then(response => {
                    if (response?.status == 200 && response?.data?.access_token) {
                        console.log(response.data.access_token);
                    }
                });
            }

        },
        signIn(email: string, password: string) {
            let formData = new FormData();
            formData.append("username", email);
            formData.append("password", password);
            // Authenticate the user.
            const responsePromise = api.post("/auth/token/", formData,
                { headers: { "Content-Type": "multipart/form-data" } }
            );
            return responsePromise;
        }
    }
})
</script>


<style>
.container {
    max-width: 500px;
    margin: 24px auto;
}
</style>