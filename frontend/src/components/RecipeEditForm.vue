<template>
    <n-form size="large">
        <editable justify-content="flex-start" @edit-complete="updateRecipeName">
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
                <div v-for="(step, idx) in form.steps">
                    <p>
                        <strong>Step {{ idx + 1 }}</strong>
                    </p>
                    <editable @edit-complete="() => editStep(step)" class="editable">
                        <template v-slot:edit-state="props">
                            <n-input
                                @input="value => updateStoredValue('STEP', idx, value)"
                                @blur="props.toggleEditState(false)"
                                @change="props.toggleEditState(false)"
                                :default-value="step.content"
                                type="textarea"
                                placeholder="Details"
                            ></n-input>
                        </template>
                        <template v-slot:default="props">
                            <p @click="() => props.toggleEditState(true)">{{ step.content }}</p>
                        </template>
                    </editable>
                </div>
                <n-button @click="addStep">+ Add Step</n-button>
            </div>
        </div>
    </n-form>
</template>
<script lang="ts">
import { defineComponent } from "vue";
import { NForm, NFormItem, NInput, NButton } from "naive-ui";
import { axiosConfigFactory, DefaultApiFactory } from "@/api";  // Typescript response interface
import Editable from "@/components/Editable.vue";


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
        updateRecipeName() {
            const name = this.form.name;
            API.updateRecipeRecipesRecipeIdPost(this.recipeId, { name }).then(response => {
                if (response.status == 200 && response.data?.name) {
                    this.form.name = response.data.name;
                }
            }).catch(console.error);
        },
        addStep() {
            const content = "What next?";
            // update client data first for fast change.
            this.form.steps.push({ content });
            // update step via API
            API.addStepRecipesRecipeIdStepsPost(this.recipeId, { content }).then(
                response => {
                    if (response.status == 200 && response.data) {
                        // update client steps with API response.
                        this.form.steps = response.data;
                    }
                }
            )
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
            } else {
                console.error("trying to edit ingredient without ID.");
            }
        },
        editStep(step: Step) {
            if (step.id) {
                API.updateStepRecipesStepsStepIdPost(
                    step.id, { content: step.content }).then(response => {
                        if (response.status == 200 && response.data) {
                            this.form.steps = response.data;  // update client step model with API results.
                        }
                    }
                    ).catch(console.error);
            } else {
                console.error("trying to edit step without ID.");
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
    margin: 12px 0;
}

.steps-wrapper {
    flex-basis: 75%;
    padding: 16px;
}

.steps-wrapper .editable {
    margin: 12px 0;
    padding-left: 12px;
}
</style>