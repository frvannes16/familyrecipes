<template>
    <div class="container">
        <router-link :to="{ name: 'myrecipes' }">
            <div class="back-button">&lt Back</div>
        </router-link>
        <h1>Create Recipe</h1>
        <recipe-edit-form :recipe-id="recipeInteger()"></recipe-edit-form>
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import RecipeEditForm from "@/components/RecipeEditForm.vue";
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

h1 {
    text-align: center;
}

.back-button {
    text-align: left;
}
</style>