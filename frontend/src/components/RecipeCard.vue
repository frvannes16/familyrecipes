<template>
    <n-card :title="recipe.name">By {{ recipe.author.first_name }} {{ recipe.author.last_name }}</n-card>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue";
import { NCard } from "naive-ui";
import { RecipeInDB } from "@/api";  // Typescript interface



export default defineComponent({

    name: "RecipeCard",
    components: { NCard },
    props: {
        recipe: {
            type: Object as PropType<RecipeInDB>,
            required: true,
        }
    }

})
</script>

<style scoped>
</style>