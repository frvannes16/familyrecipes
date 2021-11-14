<template>
    <h1>Create Recipe</h1>
    <div class="container">
        <recipe-create-form></recipe-create-form>
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import RecipeCreateForm from "../components/RecipeCreateForm.vue";
export default defineComponent({
    name: "CreateRecipe",
    components: { RecipeCreateForm },
})
</script>

<style>
.container {
    margin: 0 auto;
    width: 80%;
}
</style>