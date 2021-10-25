<template>
    <div class="container">
        <h1>My Recipes</h1>
        <recipe-card v-if="recipes" v-for="recipe in recipes.data" :recipe="recipe"></recipe-card>
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import RecipeCard from "../components/RecipeCard.vue";
import { PaginatedRecipes, axiosConfigFactory, DefaultApiFactory } from "../api";  // Typescript response interface

export default defineComponent({
    name: "MyRecipes",
    components: { RecipeCard },
    data() {
        return {
            recipes: {} as PaginatedRecipes
        }
    },
    methods: {
        loadAllRecipes() {
            const api = DefaultApiFactory(undefined, axiosConfigFactory().basePath);
            api.getRecipesRecipesGet(1, 10).then(response => {
                this.recipes = response.data;
            }).catch(console.error);
        }
    },
    created() {
        this.loadAllRecipes();
    }

});

</script>

<style>
</style>