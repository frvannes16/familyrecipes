<template>
    <div class="container">
        <progress-bar class="progress-bar"></progress-bar>
        <h1>My Recipes</h1>
        <n-space>
            <recipe-card
                v-if="recipes"
                v-for="recipe in recipes.data"
                :recipe="recipe"
                @click="() => showRecipe(recipe.id)"
            ></recipe-card>
        </n-space>
        <n-button type="primary" size="large" @click="createNewRecipe" class="btn">Create Recipe</n-button>
    </div>
    <div class="selected-recipe" v-if="!!selectedRecipe">
        <view-recipe :recipe="selectedRecipe"></view-recipe>
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import RecipeCard from "../components/RecipeCard.vue";
import ViewRecipe from "../components/ViewRecipe.vue";
import ProgressBar from "../components/ProgressBar.vue";
import { NButton, NSpace, useMessage } from "naive-ui";
import { PaginatedRecipes, RecipeInDB, axiosConfigFactory, DefaultApiFactory } from "../api";  // Typescript response interface
import { RouteLocationRaw } from "vue-router";



export default defineComponent({
    name: "MyRecipes",
    components: { RecipeCard, ViewRecipe, NButton, NSpace, ProgressBar },
    setup() {
        const message = useMessage();
        return {
            info(msg: string) {
                // TODO: move this into a mixin.
                message.info(msg);
            }
        }
    },
    data() {
        return {
            recipes: undefined as PaginatedRecipes | undefined,
            selectedRecipe: undefined as RecipeInDB | undefined,
        }
    },
    methods: {
        loadAllRecipes() {
            const api = DefaultApiFactory(undefined, axiosConfigFactory().basePath);
            api.getRecipesRecipesGet(1, 10).then(response => {
                this.recipes = response.data;
            }).catch(console.error);
        },
        createNewRecipe() {
            // First, create a new recipe with a generic name.
            const api = DefaultApiFactory(undefined, axiosConfigFactory().basePath);
            api.createUserRecipeRecipesPost({ name: "My New Recipe" }).then(response => {
                if (response.status == 200) {
                    this.info(`New recipe created: 'My New Recipe'`,
                        { keepAliveOnHover: true });
                    // Then navigate to the recipe edit page.
                    const to: RouteLocationRaw = {
                        name: 'editrecipe',
                        params: {
                            recipeId: response.data.id,
                        }
                    };
                    this.$router.push(to);
                } else {
                    console.error(response);
                }
            }
            )

        },
        showRecipe(recipeId: Number) {
            if (this.recipes) {
                const selectedRecipe = this.recipes.data.find(recipe => recipe.id == recipeId);
                if (!!selectedRecipe) {
                    this.selectedRecipe = selectedRecipe;
                } else {
                    console.error("Unknown recipe selected with ID " + String(recipeId));
                }
            }
        }
    },
    created() {
        this.loadAllRecipes();
        console.log(this.selectedRecipe);
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