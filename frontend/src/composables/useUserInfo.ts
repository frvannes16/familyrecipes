import { reactive, readonly } from "vue";
import { AuthenticatedUser, axiosConfigFactory, DefaultApiFactory } from "@/api";

interface UserInfoState {
    currentUser: AuthenticatedUser | undefined,
    loading: boolean,
    loaded: boolean
}

const state: UserInfoState = reactive({
    currentUser: undefined,
    loading: false,
    loaded: false
});

export default function useUserInfo() {
    const API = DefaultApiFactory(undefined, axiosConfigFactory().basePath);

    const loadUserInfo = () => {
        return new Promise<UserInfoState>((resolve, reject) => {
            if (!state.loaded) {
                state.loading = true;
                const userInfoResponse = API.getMyUserUsersMeGet();
                userInfoResponse.then(response => {
                    state.currentUser = response.data;
                    state.loading = false;
                    state.loaded = true;
                    resolve(readonly(state));
                }).catch(error => {
                    state.loading = false;
                    state.loaded = false;
                    console.error(error);
                    reject(error);
                });
            } else {
                resolve(readonly(state));
            }
        })
    };

    return { userState: readonly(state), loadUserInfo };

};
