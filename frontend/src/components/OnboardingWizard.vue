<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

defineProps<{ show: boolean }>()
const emit = defineEmits<{ close: [] }>()

const router = useRouter()
const currentStep = ref(1)
const totalSteps = 4
const showHelperText = ref(false)

function nextStep() {
  if (currentStep.value < totalSteps) {
    currentStep.value++
  }
}

function selectComparator(_type: string) {
  currentStep.value = 4
}

function finish() {
  emit('close')
  router.push('/feeds-in/new')
}
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="emit('close')">
        <Transition name="slide" mode="out-in">
          <div :key="currentStep" class="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 p-8 relative">
            <!-- Progress dots -->
            <div class="flex justify-center gap-2 mb-8">
              <span
                v-for="step in totalSteps"
                :key="step"
                class="w-2.5 h-2.5 rounded-full transition-colors duration-300"
                :class="step === currentStep ? 'bg-indigo-600' : step < currentStep ? 'bg-indigo-300' : 'bg-gray-200'"
              />
            </div>

            <!-- Step 1: Welcome -->
            <div v-if="currentStep === 1" class="text-center">
              <div class="text-4xl mb-4">&#128075;</div>
              <h2 class="text-2xl font-bold text-gray-900 mb-3">Witaj w Feedy!</h2>
              <p class="text-gray-600 mb-8">Za chwile skonfigurujesz swoj pierwszy feed produktowy.</p>
              <button
                @click="nextStep"
                class="w-full px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors cursor-pointer"
              >
                Zaczynamy &rarr;
              </button>
            </div>

            <!-- Step 2: XML link -->
            <div v-if="currentStep === 2">
              <h2 class="text-2xl font-bold text-gray-900 mb-3 text-center">Wklej link do XML</h2>
              <p class="text-gray-600 mb-4">
                Skopiuj link do XML z panelu swojego sklepu (Shoper, WooCommerce, PrestaShop).
              </p>
              <div class="bg-gray-50 border border-gray-200 rounded-lg p-3 mb-4 font-mono text-sm text-gray-700 break-all">
                https://twojsklep.pl/.../GoogleProductSearch
              </div>
              <button
                @click="nextStep"
                class="w-full px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors mb-3 cursor-pointer"
              >
                Juz mam link, dalej &rarr;
              </button>
              <button
                @click="showHelperText = !showHelperText"
                class="w-full text-sm text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer"
              >
                {{ showHelperText ? 'Ukryj pomoc' : 'Nie mam linka, pokaz jak go znalezc' }}
              </button>
              <Transition name="expand">
                <div v-if="showHelperText" class="mt-4 p-4 bg-indigo-50 border border-indigo-100 rounded-lg text-sm text-gray-700">
                  <p class="font-semibold text-indigo-800 mb-2">Shoper:</p>
                  <ol class="list-decimal list-inside space-y-1">
                    <li>Zaloguj sie do panelu Shoper</li>
                    <li>Przejdz do <span class="font-medium">Integracja</span></li>
                    <li>Wybierz <span class="font-medium">Google Product Search</span></li>
                    <li>Skopiuj wygenerowany link XML</li>
                  </ol>
                </div>
              </Transition>
            </div>

            <!-- Step 3: Choose comparator -->
            <div v-if="currentStep === 3">
              <h2 class="text-2xl font-bold text-gray-900 mb-3 text-center">Wybierz porownywarke</h2>
              <p class="text-gray-600 mb-6 text-center">
                Feedy automatycznie zmapuje pola Twojego XML na format wymagany przez porownywarke.
              </p>
              <div class="grid grid-cols-3 gap-3">
                <button
                  @click="selectComparator('ceneo')"
                  class="flex flex-col items-center p-4 border-2 border-gray-200 rounded-xl hover:border-indigo-500 hover:bg-indigo-50 transition-colors cursor-pointer"
                >
                  <div class="text-2xl mb-2">&#128722;</div>
                  <span class="font-semibold text-gray-900 text-sm">Ceneo</span>
                </button>
                <button
                  @click="selectComparator('gmc')"
                  class="flex flex-col items-center p-4 border-2 border-gray-200 rounded-xl hover:border-indigo-500 hover:bg-indigo-50 transition-colors cursor-pointer"
                >
                  <div class="text-2xl mb-2">&#127758;</div>
                  <span class="font-semibold text-gray-900 text-sm">Google Merchant Center</span>
                </button>
                <button
                  @click="selectComparator('custom')"
                  class="flex flex-col items-center p-4 border-2 border-gray-200 rounded-xl hover:border-indigo-500 hover:bg-indigo-50 transition-colors cursor-pointer"
                >
                  <div class="text-2xl mb-2">&#9881;&#65039;</div>
                  <span class="font-semibold text-gray-900 text-sm">Custom</span>
                </button>
              </div>
            </div>

            <!-- Step 4: Done -->
            <div v-if="currentStep === 4" class="text-center">
              <div class="text-4xl mb-4">&#127881;</div>
              <h2 class="text-2xl font-bold text-gray-900 mb-3">Gotowe!</h2>
              <p class="text-gray-600 mb-8">
                Twoj feed bedzie dostepny pod unikalnym linkiem. Wklej go w panelu porownywarki.
              </p>
              <button
                @click="finish"
                class="w-full px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors cursor-pointer"
              >
                Przejdz do panelu
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.25s ease;
}
.slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}
.expand-enter-to,
.expand-leave-from {
  max-height: 200px;
}
</style>
