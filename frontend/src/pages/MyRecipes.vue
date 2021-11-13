<template>
    <div class="container">
        <h1>My Recipes</h1>
        <recipe-card
            v-if="recipes"
            v-for="recipe in recipes.data"
            :recipe="recipe"
            @click="() => showRecipe(recipe.id)"
        ></recipe-card>
        <n-button
            type="primary"
            size="large"
            @click="navToCreateRecipePage"
            class="btn"
        >Create Recipe</n-button>
    </div>
    <div class="selected-recipe" v-if="!!selectedRecipe">
        <view-recipe :recipe="selectedRecipe"></view-recipe>
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import RecipeCard from "../components/RecipeCard.vue";
import ViewRecipe from "../components/ViewRecipe.vue";
import { NButton, NSpace } from "naive-ui";
import { PaginatedRecipes, RecipeInDB, axiosConfigFactory, DefaultApiFactory } from "../api";  // Typescript response interface
import { RouteLocationRaw, } from "vue-router";

export default defineComponent({
    name: "MyRecipes",
    components: { RecipeCard, ViewRecipe, NButton, NSpace },
    data() {
        return {
            recipes: undefined as PaginatedRecipes | undefined ,
            selectedRecipe: undefined  as RecipeInDB | undefined,
        }
    },
    methods: {
        loadAllRecipes() {
            const api = DefaultApiFactory(undefined, axiosConfigFactory().basePath);
            api.getRecipesRecipesGet(1, 10).then(response => {
                this.recipes = response.data;
            }).catch(console.error);
        },
        navToCreateRecipePage() {
            const to: RouteLocationRaw = {
                name: 'newrecipe'
            };
            this.$router.push(to);
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

<style>
.btn {
    margin: 24px 0;
}
</style>