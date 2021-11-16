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
    </div>
</template>
<script lang="ts">
import { defineComponent, PropType } from "vue";
import { Configuration, RecipeInDB } from "../api";
import { NButton } from "naive-ui";
import { axiosConfigFactory, DefaultApiFactory } from "../api";  // Typescript response interface


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
            /** Generates a PDF file and forces the browser to download the file. */
            console.log(`Generating cookbook for recipe "${this.recipe.name}"`);
            const api = DefaultApiFactory(new Configuration({ baseOptions: { responseType: 'blob' } }), axiosConfigFactory().basePath);

            api.generateRecipePdfRecipesRecipeIdGeneratePdfGet(this.recipe.id).then(response => {
                // Force browser to download PDF.
                // From https://stackoverflow.com/questions/41938718/how-to-download-files-using-axios
                // See https://gist.github.com/javilobo8/097c30a233786be52070986d8cdb1743 to understand these quirks.
                const link = document.createElement('a');
                link.href = URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
                link.download = 'recipe.pdf';
                document.body.appendChild(link);
                link.click();

                link.remove();
                // in case the blob uses a lot of memory
                setTimeout(() => URL.revokeObjectURL(link.href), 2000);
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