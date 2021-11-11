<template>
    <div class="recipe-wrapper">
        <h2 v-if="recipe.name">{{ recipe.name }}</h2>
        <h3
            v-if="recipe.author?.first_name"
        >By {{ recipe.author?.first_name }} {{ recipe.author?.last_name }}</h3>
        <h3>Steps:</h3>
        <p>{{ recipe.steps }}</p>
        <n-button type="primary" size="large" @click="generateCookbookPdf" class="btn">Make Cookbook</n-button>
    </div>
</template>
<script lang="ts">
import { defineComponent, PropType } from "vue";
import { RecipeInDB } from "../api";
import { NButton } from "naive-ui";

export default defineComponent({
    name: "ViewRecipe",
    components: { NButton },
    props: {
        recipe: {
            type: Object as PropType<RecipeInDB>,
            required: true,
        }
    },
    methods: {
        generateCookbookPdf() {
            console.log(`Generating cookbook for recipe "${this.recipe.name}"`);
        }
    }
});
</script>

<style>
.recipe-wrapper {
    text-align: left;
    width: 60vw;
    margin: 0 auto;
}
</style>