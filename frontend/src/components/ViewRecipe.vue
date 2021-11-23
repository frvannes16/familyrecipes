<template>
    <div class="recipe-wrapper">
        <h2 v-if="recipe.name">{{ recipe.name }}</h2>
        <h3
            v-if="recipe.author?.first_name"
        >By {{ recipe.author?.first_name }} {{ recipe.author?.last_name }}</h3>
        <h3>Ingredients:</h3>
        <ul>
            <li
                v-for="ingredient in recipe.ingredients"
                :key="ingredient.id"
            >{{ ingredient.content }}</li>
        </ul>
        <h3>Steps:</h3>
        <ol>
            <li v-for="step in recipe.steps">{{ step.content }}</li>
        </ol>
        <n-space>
            <n-button
                type="primary"
                size="large"
                @click="$router.push({ name: 'editrecipe', params: { recipeId: recipe.id } })"
                class="btn"
            >Edit Recipe</n-button>
            <n-button
                type="default"
                size="large"
                @click="generateCookbookPdf"
                class="btn"
            >Make Recipe Card</n-button>
        </n-space>
    </div>
</template>
<script lang="ts">
import { defineComponent, PropType } from "vue";
import { NButton, NSpace } from "naive-ui";
import { axiosConfigFactory, DefaultApiFactory, Configuration, RecipeInDB } from "@/api";
import downloadPdfInBackground from "@/utils/pdf";


export default defineComponent({
    name: "ViewRecipe",
    components: { NButton, NSpace },
    props: {
        recipe: {
            type: Object as PropType<RecipeInDB>,
            required: true,
        }
    },
    methods: {
        generateCookbookPdf() {
            /** Generates a PDF file and forces the browser to download the file. */
            const api = DefaultApiFactory(new Configuration({ baseOptions: { responseType: 'blob' } }), axiosConfigFactory().basePath);

            api.generateRecipePdfRecipesRecipeIdGeneratePdfGet(this.recipe.id).then(response => {
                downloadPdfInBackground(response.data, 'recipe.pdf');
            }).catch(console.error);
        }
    }
});
</script>

<style scoped>
.recipe-wrapper {
    text-align: left;
    width: 60vw;
    margin: 0 auto;
}
</style>