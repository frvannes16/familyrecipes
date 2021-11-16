import { createRouter, createWebHistory, RouterOptions } from "vue-router";

const LoginPage = () => import("../pages/Login.vue");
const MyRecipesPage = () => import("../pages/MyRecipes.vue");
const EditRecipePage = () => import("../pages/EditRecipe.vue");

const options: RouterOptions = {
    history: createWebHistory(),
    routes: [
        {
            path: "/",
            redirect: "/login"
        },
        {
            path: '/login',
            name: 'login',
            component: LoginPage,
        },
        {
            path: '/recipes/me',
            name: 'myrecipes',
            component: MyRecipesPage,
        },
        {
            path: '/recipes/:recipeId/edit',
            name: "editrecipe",
            component: EditRecipePage,
        }

    ]
};

const router = createRouter(options)

export default router;