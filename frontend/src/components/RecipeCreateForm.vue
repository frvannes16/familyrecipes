<template>
    <n-form :label-width="80" size="large">
        <n-form-item label="Recipe Name" path="form.name">
            <n-input v-model="form.name" placeholder="Recipe Name"></n-input>
        </n-form-item>
        <h3>Ingredients</h3>
        <n-form-item v-for="(ingredient, idx) in form.ingredients" :label="`Ingredient ${idx+1}`" path="ingredient.content">
            <n-input v-model="ingredient.quantity" placeholder="1, 1/2, 12"></n-input>
            <n-input v-model="ingredient.unit" placeholder="cup/tsp/tbsp/kg"></n-input>
            <n-input v-model="ingredient.item" placeholder="Tomatoes..."></n-input>
        </n-form-item>
        <n-button @click="addIngredient">+</n-button>
        <h3>Steps</h3>
        <n-form-item v-for="(step, idx) in form.steps" :label="`Step ${idx+1}`" path="step.content">
            <n-input v-model="step.content" placeholder="Details"></n-input>
        </n-form-item>
        <n-button @click="addStep">+</n-button>
        
    </n-form>
</template>
<script lang="ts">
import { defineComponent } from "vue";
import {NForm, NFormItem, NInput, NButton} from "naive-ui";

interface Step {
    content: String
};

interface Ingredient {
    quantity: String,
    unit: String,
    item: String

}

export default defineComponent({
    name: "RecipeCreateForm",
    components: {NForm, NFormItem, NInput, NButton},
    data() {
        return {
            form: {
                name: "" as String,
                steps: [] as Array<Step>,
                ingredients: [] as Array<Ingredient>
            }
        }
    },
    methods: {
        addStep() {
            this.form.steps.push({content: ""});
        },
        addIngredient() {
            this.form.ingredients.push({
                quantity: "1",
                unit: "",
                item: ""
            })
        }
    }
});
</script>