<template>
    <n-form size="large">
        <editable justify-content="flex-start">
            <template v-slot:default="props">
                <h2 class="recipe-name" @click="() => props.toggleEditState(true)">{{ form.name }}</h2>
            </template>
            <template v-slot:edit-state="props">
                <n-input
                    @input="value => form.name = value"
                    :default-value="form.name"
                    class="recipe-name"
                    placeholder="Recipe Name"
                    @blur="() => props.toggleEditState(false)"
                ></n-input>
            </template>
        </editable>
        <div class="recipe-wrapper">
            <div class="ingredients-wrapper">
                <h3>Ingredients</h3>

                <editable
                    v-for="(ingredient, idx) in form.ingredients"
                    height="35px"
                    class="editable"
                    @edit-complete="() => editIngredient(ingredient)"
                >
                    <template v-slot:edit-state="props">
                        <n-input
                            @input="value => updateStoredValue('INGREDIENT', idx, value)"
                            @blur="() => props.toggleEditState(false)"
                            :default-value="ingredient.content"
                            placeholder="1 3/4 tsp cayenne powder"
                        ></n-input>
                    </template>
                    <template v-slot:default="props">
                        <p @click="() => props.toggleEditState(true)">{{ ingredient.content }}</p>
                    </template>
                </editable>
                <n-button @click="addIngredient">+ Add Ingredient</n-button>
            </div>
            <div class="steps-wrapper">
                <h3>Steps</h3>
                <n-form-item
                    v-for="(step, idx) in form.steps"
                    :label="`Step ${idx + 1} `"
                    path="step.content"
                >
                    <n-input
                        @input="value => updateStoredValue('STEP', idx, value)"
                        :default-value="step.content"
                        type="textarea"
                        placeholder="Details"
                    ></n-input>
                </n-form-item>
                <n-button @click="addStep">+ Add Step</n-button>
            </div>
        </div>
    </n-form>
</template>
<script lang="ts">
import { defineComponent } from "vue";
import { NForm, NFormItem, NInput, NButton } from "naive-ui";
import { axiosConfigFactory, DefaultApiFactory } from "../api";  // Typescript response interface
import Editable from "./Editable.vue";


interface Step {
    id?: number
    content: string
};

interface Ingredient {
    id?: number
    content: string
}

type STORED_VAL_TYPE = "INGREDIENT" | "STEP";
const API = DefaultApiFactory(undefined, axiosConfigFactory().basePath);



export default defineComponent({
    name: "RecipeEditForm",
    components: { NForm, NFormItem, NInput, NButton, Editable },
    props: {
        recipeId: {
            type: Number,
            required: true
        }
    },
    data() {
        return {
            form: {
                name: "",
                steps: [] as Array<Step>,
                ingredients: [] as Array<Ingredient>
            }
        }
    },
    created() {
        API.getSingleRecipeRecipesRecipeIdGet(this.recipeId).then(response => {
            if (response.status == 200) {
                this.form.name = response.data.name;
                this.form.steps = response.data.steps;
                this.form.ingredients = response.data.ingredients;
            }
        })
    },
    methods: {
        addStep() {
            this.form.steps.push({ content: "What next?" });
        },
        addIngredient() {
            const content = "New Ingredient";
            // update client data first.
            this.form.ingredients.push({
                content
            });
            // update API
            API.addIngredientRecipesRecipeIdIngredientsPost(this.recipeId, { content }).then(
                response => {
                    if (response.status == 200 && response.data) {
                        // update client ingredient model with API results.
                        this.form.ingredients = response.data;
                    }
                }
            )
        },
        editIngredient(ingredient: Ingredient) {
            if (ingredient.id) {
                API.updateIngredientRecipesIngredientsIngredientIdPost(
                    ingredient.id, { content: ingredient.content }).then(response => {
                        if (response.status == 200 && response.data) {
                            this.form.ingredients = response.data;  // update client ingredient model with API results.
                        }
                    }
                    ).catch(console.error);
            }
        },
        updateStoredValue(valueType: STORED_VAL_TYPE, index: number, value: string) {
            switch (valueType) {
                case "INGREDIENT":
                    this.form.ingredients[index].content = value;
                    break;
                case "STEP":
                    this.form.steps[index].content = value;
                default:
                    break;
            }
        }
    }
});
</script>

<style scoped>
.recipe-name {
    margin-right: 16px;
}
.recipe-wrapper {
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
}

.ingredients-wrapper {
    flex-basis: 25%;
    padding: 16px;
}

.ingredients-wrapper .editable {
    margin: 8px 0;
}

.steps-wrapper {
    flex-basis: 75%;
    padding: 16px;
}
</style>