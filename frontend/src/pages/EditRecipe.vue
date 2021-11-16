<template>
    <h1>Create Recipe</h1>
    <div class="container">
        <recipe-edit-form :recipe-id="recipeInteger()"></recipe-edit-form>
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import RecipeEditForm from "../components/RecipeEditForm.vue";
export default defineComponent({
    name: "EditRecipe",
    components: { RecipeEditForm },
    methods: {
        recipeInteger() {
            const recipeIdParam = this.$route.params.recipeId;
            if (Array.isArray(recipeIdParam)) {
                console.error("RecipeID is of type array. Not good!");
                return 0
            } else {
                return Number.parseInt(recipeIdParam)
            }
        }
    }
})
</script>

<style scoped>
.container {
    margin: 0 auto;
    width: 80%;
    text-align: left;
}
</style>