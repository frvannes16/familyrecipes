<template>
    <h1>Create Recipe</h1>
    <div class="container">
        <recipe-edit-form :recipe-id="$route.params.recipeId"></recipe-edit-form>
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import RecipeEditForm from "../components/RecipeEditForm.vue";
export default defineComponent({
    name: "EditRecipe",
    components: { RecipeEditForm },
})
</script>

<style scoped>
.container {
    margin: 0 auto;
    width: 80%;
    text-align: left;
}
</style>