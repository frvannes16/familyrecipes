<template>
    <div class="container">
        <progress-bar class="progress-bar"></progress-bar>
        <h1>My Recipes</h1>
        <n-space>
            <recipe-card
                v-if="recipes"
                v-for="recipe in recipes.data"
                :recipe="recipe"
                @click="() => showSelectedRecipe(recipe.id)"
            ></recipe-card>
        </n-space>
        <n-button type="primary" size="large" @click="createNewRecipe" class="btn">Create Recipe</n-button>
    </div>
    <div class="selected-recipe" v-if="!!selectedRecipe">
        <view-recipe :recipe="selectedRecipe"></view-recipe>
    </div>
    <n-button v-if="recipes" @click="generateCookbook">Make Cookbook</n-button>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";
import { RouteLocationRaw, useRouter } from "vue-router";
import { NButton, NSpace, useMessage } from "naive-ui";
import { PaginatedRecipes, RecipeInDB, axiosConfigFactory, DefaultApiFactory, Configuration } from "@/api";  // Typescript response interface
import RecipeCard from "@/components/RecipeCard.vue";
import ViewRecipe from "@/components/ViewRecipe.vue";
import ProgressBar from "@/components/ProgressBar.vue";
import useUserInfo from "@/composables/useUserInfo";
import downloadPdfInBackground from "@/utils/pdf";



export default defineComponent({
    name: "MyRecipes",
    components: { RecipeCard, ViewRecipe, NButton, NSpace, ProgressBar },
    setup() {
        const API = DefaultApiFactory(undefined, axiosConfigFactory().basePath);
        const PDF_API = DefaultApiFactory(new Configuration({ baseOptions: { responseType: 'blob' } }), axiosConfigFactory().basePath);
        const message = useMessage();
        const router = useRouter();
        const { userState, loadUserInfo } = useUserInfo();


        // Recipes
        const recipes = ref<PaginatedRecipes | undefined>(undefined);
        const loadAllRecipes = () => {
            API.getRecipesRecipesGet(1, 10).then(response => {
                recipes.value = response.data;
            }).catch(console.error);
        };

        const createNewRecipe = () => {
            // First, create a new recipe with a generic name.
            API.createUserRecipeRecipesPost({ name: "My New Recipe" }).then(response => {
                if (response.status == 200) {
                    message.info(`New recipe created: 'My New Recipe'`,
                        { keepAliveOnHover: true });
                    // Then navigate to the recipe edit page.
                    const to: RouteLocationRaw = {
                        name: 'editrecipe',
                        params: {
                            recipeId: response.data.id,
                        }
                    };
                    router.push(to);
                } else {
                    console.error(response);
                }
            }
            )
        };

        // Show Recipe
        const selectedRecipe = ref<RecipeInDB | undefined>(undefined);
        const showSelectedRecipe = (recipeId: Number) => {
            if (recipes.value?.data) {
                const targetRecipe = recipes.value?.data.find(recipe => recipe.id == recipeId);
                if (targetRecipe) {
                    selectedRecipe.value = targetRecipe;
                } else {
                    console.error("Unknown recipe selected with ID " + String(recipeId));
                }
            }
        };

        // Generate cookbook from all recipes.

        const generateCookbook = () => {
            if (!userState.loaded || !userState.currentUser?.id) {
                // load user data and retry.
                loadUserInfo().then(() => {
                    generateCookbook()
                }).catch(error => {
                    console.error("User ID not available to generate user cookbook PDF.");
                    message.error("Error encountered when generating user cookbook. Please try again later.");
                });
            }
            else {
                PDF_API.generateUserRecipesPdfUsersAuthorIdRecipesGeneratePdfGet(userState.currentUser.id).then(response => {
                    downloadPdfInBackground(response.data, 'cookbook.pdf');
                }).catch(error => {
                    console.error(error);
                    if (error.response.data?.detail) {
                        message.error(error.response.data.detail);
                    } else {
                        message.error("Could not generate cookbook. Please try again later.");
                    }
                });
            }
        };

        // Init procedures
        loadAllRecipes();

        return {
            recipes,
            selectedRecipe,
            showSelectedRecipe,
            createNewRecipe,
            generateCookbook
        };
    }
});

</script>

<style scoped>
.progress-bar {
    margin: 12px auto;
    text-align: center;
}
.container {
    width: 80%;
    margin: 0 auto;
}
.btn {
    margin: 24px 0;
}
</style>