<template>
    <div class="container">
        <n-card>
            <n-tabs default-value="signin" size="large">
                <n-tab-pane name="signin" tab="Sign in">
                    <n-form :model="signInFormVals" :rules="signInFormRules" ref="signInFormRef">
                        <n-form-item-row path="email">
                            <n-input v-model:value="signInFormVals.email" placeholder="Email" />
                        </n-form-item-row>
                        <n-form-item-row path="password">
                            <n-input
                                v-model:value="signInFormVals.password"
                                type="password"
                                show-password-on="mousedown"
                                placeholder="Password"
                                @change="onSignIn"
                            />
                        </n-form-item-row>
                    </n-form>
                    <n-button type="primary" block @click="onSignIn">Sign In</n-button>
                </n-tab-pane>
                <n-tab-pane name="signup" tab="Sign Up">
                    <n-form ref="signUpFormRef" :rules="signUpFormRules" :model="signUpFormVals">
                        <n-form-item-row path="email">
                            <n-input v-model:value="signUpFormVals.email" placeholder="Email" />
                        </n-form-item-row>
                        <n-form-item-row>
                            <n-input
                                v-model:value="signUpFormVals.first_name"
                                placeholder="First Name"
                            />
                            <n-input
                                v-model:value="signUpFormVals.last_name"
                                placeholder="Last Name"
                            />
                        </n-form-item-row>
                        <n-form-item-row path="password">
                            <n-input
                                v-model:value="signUpFormVals.password"
                                type="password"
                                show-password-on="mousedown"
                                :min-length="MIN_PASSWORD_LENGTH"
                                placeholder="Password"
                            />
                        </n-form-item-row>
                        <n-form-item-row path="confirmPassword">
                            <n-input
                                v-model:value="signUpFormVals.confirmPassword"
                                type="password"
                                show-password-on="mousedown"
                                :min-length="MIN_PASSWORD_LENGTH"
                                placeholder="Confirm password"
                                @change="onSignUp"
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
import { RouteLocationRaw, useRouter } from "vue-router";
import { NButton, NInput, NForm, NFormItem, NTabs, NTabPane, NFormItemRow, NCard } from 'naive-ui';
import useSignIn from "@/composables/useSignIn";
import useSignUp from "@/composables/useSignUp";

export default defineComponent({
    components: { NButton, NInput, NForm, NFormItem, NTabs, NTabPane, NFormItemRow, NCard },
    setup() {
        const MIN_PASSWORD_LENGTH = 12;
        const router = useRouter();

        // Navigation
        const navigateToUserPage = () => {
            const to: RouteLocationRaw = {
                name: 'myrecipes'
            };
            router.push(to);  // TODO: unhandled promise
        };

        const { formRef: signInFormRef, formRules: signInFormRules, formVals: signInFormVals, onSignIn } = useSignIn();
        const { formRef: signUpFormRef, formRules: signUpFormRules, formVals: signUpFormVals, onSignUp } = useSignUp();



        return {
            MIN_PASSWORD_LENGTH,
            signInFormRef,
            signInFormRules,
            signInFormVals,
            onSignIn: onSignIn(navigateToUserPage),
            signUpFormRef,
            signUpFormRules,
            signUpFormVals,
            onSignUp: onSignUp(navigateToUserPage)
        }
    },
})
</script>


<style scoped>
.container {
    max-width: 500px;
    margin: 24px auto;
}
</style>