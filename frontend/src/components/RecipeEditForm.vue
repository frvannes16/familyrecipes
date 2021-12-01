<template>
    <n-form size="large">
        <editable justify-content="flex-start" @edit-complete="updateRecipeName">
            <template v-slot:default="props">
                <h2 class="recipe-name" @click="() => props.toggleEditState(true)">{{ form.name }}</h2>
            </template>
            <template v-slot:edit="{editor, toggleEditState}">
                <n-input
                    @input="value => form.name = value"
                    :default-value="form.name"
                    class="recipe-name"
                    placeholder="Recipe Name"
                    @blur="() => toggleEditState(false)"
                    ref="editor"
                ></n-input>
            </template>
        </editable>
        <div class="recipe-wrapper">
            <div class="ingredients-wrapper">
                <h3>Ingredients</h3>
                <editable
                    v-for="(ingredient, idx) in form.ingredients"
                    :key="idx"
                    :ref="addEditableRef"
                    height="35px"
                    class="editable"
                    @edit-complete="() => editIngredient(ingredient)"
                >
                    <template v-slot:edit="props">
                        <n-input
                            @input="value => updateStoredValue('INGREDIENT', idx, value)"
                            @blur="() => props.toggleEditState(false)"
                            :default-value="ingredient.content"
                            :autofocus="true"
                            :passively-activated="true"
                            placeholder="1 3/4 tsp cayenne powder"
                            ref="props.editor"
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
                        <template v-slot:edit="props">
                            <n-input
                                @input="value => updateStoredValue('STEP', idx, value)"
                                @blur="props.toggleEditState(false)"
                                @change="props.toggleEditState(false)"
                                :autofocus="true"
                                :default-value="step.content"
                                type="textarea"
                                placeholder="Details"
                                ref="props.editor"
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
import { defineComponent, reactive, ref, onBeforeUpdate } from "vue";
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
    setup(props) {
        const form = reactive({
            name: "",
            steps: [] as Array<Step>,
            ingredients: [] as Array<Ingredient>,
            focusedIngredientIdx: null as null | Number
        });

        const editableRefs = ref([]);

        const addEditableRef = (el) => {
            if (el) {
                editableRefs.value.push(el);
            }
        };

        onBeforeUpdate(() => {
            editableRefs.value = [];
        });

        // Fetch recipe data
        API.getSingleRecipeRecipesRecipeIdGet(props.recipeId).then(response => {
            if (response.status == 200) {
                form.name = response.data.name;
                form.steps = response.data.steps;
                form.ingredients = response.data.ingredients;
            }
        })

        const updateRecipeName = () => {
            const name = form.name;
            API.updateRecipeRecipesRecipeIdPost(props.recipeId, { name }).then(response => {
                if (response.status == 200 && response.data?.name) {
                    form.name = response.data.name;
                }
            }).catch(console.error);
        };

        const addStep = () => {
            const content = "What next?";
            // update client data first for fast change.
            form.steps.push({ content });
            // update step via API
            API.addStepRecipesRecipeIdStepsPost(props.recipeId, { content }).then(
                response => {
                    if (response.status == 200 && response.data) {
                        // update client steps with API response.
                        form.steps = response.data;
                    }
                }
            )
        };

        const addIngredient = () => {
            const content = "New Ingredient";
            // update client data first.
            form.ingredients.push({
                content
            });

            // update API
            API.addIngredientRecipesRecipeIdIngredientsPost(props.recipeId, { content }).then(
                response => {
                    if (response.status == 200 && response.data) {
                        // update client ingredient model with API results.
                        form.ingredients = response.data;
                    }
                }
            );
        };

        const editIngredient = (ingredient: Ingredient) => {
            if (ingredient.id) {
                API.updateIngredientRecipesIngredientsIngredientIdPost(
                    ingredient.id, { content: ingredient.content }).then(response => {
                        if (response.status == 200 && response.data) {
                            form.ingredients = response.data;  // update client ingredient model with API results.
                        }
                    }
                    ).catch(console.error);
            } else {
                console.error("trying to edit ingredient without ID.");
            }
        };

        const editStep = (step: Step) => {
            if (step.id) {
                API.updateStepRecipesStepsStepIdPost(
                    step.id, { content: step.content }).then(response => {
                        if (response.status == 200 && response.data) {
                            form.steps = response.data;  // update client step model with API results.
                        }
                    }
                    ).catch(console.error);
            } else {
                console.error("trying to edit step without ID.");
            }
        };

        const updateStoredValue = (valueType: STORED_VAL_TYPE, index: number, value: string) => {
            switch (valueType) {
                case "INGREDIENT":
                    form.ingredients[index].content = value;
                    break;
                case "STEP":
                    form.steps[index].content = value;
                default:
                    break;
            }
        }

        return {
            form,
            updateRecipeName,
            addStep,
            editStep,
            addIngredient,
            editIngredient,
            updateStoredValue,
            editableRefs,
            addEditableRef
        }
    },
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