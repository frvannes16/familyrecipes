<template>
    <div class="container">
        <n-card>
            <n-tabs default-value="signIn" size="large">
                <n-tab-pane name="signin" tab="Sign in">
                    <n-form>
                        <n-form-item-row>
                            <n-input v-model:value="signIn.email" placeholder="Email" />
                        </n-form-item-row>
                        <n-form-item-row>
                            <n-input
                                v-model:value="signIn.password"
                                type="password"
                                show-password-on="mousedown"
                                placeholder="Password"
                                @change="onSignIn(navigateToUserPage)"
                            />
                        </n-form-item-row>
                    </n-form>
                    <n-button type="primary" block @click="onSignIn(navigateToUserPage)">Sign In</n-button>
                </n-tab-pane>
                <n-tab-pane name="signup" tab="Sign Up">
                    <n-form>
                        <n-form-item-row>
                            <n-input v-model:value="signUp.email" placeholder="Email" />
                        </n-form-item-row>
                        <n-form-item-row>
                            <n-input
                                v-model:value="signUp.password"
                                type="password"
                                show-password-on="mousedown"
                                :min-length="MIN_PASSWORD_LENGTH"
                                placeholder="Password"
                            />
                        </n-form-item-row>
                        <n-form-item-row>
                            <n-input
                                v-model:value="signUp.confirmPassword"
                                type="password"
                                show-password-on="mousedown"
                                :min-length="MIN_PASSWORD_LENGTH"
                                placeholder="Confirm password"
                                @change="onSignUp(navigateToUserPage)"
                            />
                        </n-form-item-row>
                    </n-form>
                    <n-button type="primary" block @click="onSignUp(navigateToUserPage)">Sign Up</n-button>
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

        const { signIn, onSignIn } = useSignIn();
        const { signUp, onSignUp } = useSignUp();


        return {
            MIN_PASSWORD_LENGTH,
            signIn,
            onSignIn,
            signUp,
            onSignUp,
            navigateToUserPage
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