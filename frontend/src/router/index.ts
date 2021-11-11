import { createRouter, createWebHistory, RouterOptions } from "vue-router";

const LoginPage = () => import("../pages/Login.vue");
const MyRecipesPage = () => import("../pages/MyRecipes.vue");
const NewRecipePage = () => import("../pages/CreateRecipe.vue");

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
            path: '/recipes/new',
            name: "newrecipe",
            component: NewRecipePage,
        }

    ]
};

const router = createRouter(options)

export default router;