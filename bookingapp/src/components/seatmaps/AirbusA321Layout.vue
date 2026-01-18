<template>
  <div class="p-8 bg-slate-100 min-h-screen">
    <div class="max-w-5xl mx-auto bg-white rounded-[100px] shadow-2xl border-x-[16px] border-slate-700 p-12 relative overflow-hidden">
      
      <div class="flex justify-between items-center mb-10 border-b-2 border-slate-100 pb-8">
        <div class="flex gap-4">
          <div class="flex flex-col items-center gap-1">
             <div class="w-14 h-14 bg-blue-50 rounded-xl flex items-center justify-center border-2 border-blue-100">
               <span class="text-[10px] font-bold text-blue-800">GALLEY</span>
             </div>
             <span class="text-[8px] text-slate-400 font-bold uppercase">Front</span>
          </div>
          <div class="w-14 h-14 bg-slate-800 rounded-xl flex items-center justify-center">
             <span class="text-white text-[18px]">🚻</span>
          </div>
        </div>
        <div class="text-right">
          <h2 class="text-3xl font-black text-blue-900 leading-none">A321neo LR</h2>
          <p class="text-[10px] font-bold text-slate-400 tracking-[0.2em] uppercase mt-2">Long Range Config</p>
        </div>
      </div>

      <div class="relative flex flex-col gap-1">
        
        <div class="grid grid-cols-7 gap-3 mb-6 px-12 text-center font-black text-slate-300 text-xs">
          <span>A</span><span>B</span><span>C</span>
          <div class="text-blue-100 text-[8px] self-center uppercase tracking-widest">Aisle</div>
          <span>H</span><span>J</span><span>K</span>
        </div>

        <div class="mb-12 relative px-12">
          <div class="absolute -left-2 top-0 bottom-0 w-1 bg-blue-600 rounded-full opacity-20"></div>
          <div v-for="row in [1, 2, 3]" :key="row" class="grid grid-cols-7 gap-3 mb-4 items-center">
            <div class="text-[10px] font-bold text-slate-300 text-center">{{ row }}</div>
            <button @click="selectSeat(row, 'A')" :class="getSeatClass(row, 'A', true)">A</button>
            <div class="h-10"></div> <button @click="selectSeat(row, 'C')" :class="getSeatClass(row, 'C', true)">C</button>
            <div class="w-full h-1"></div> <button @click="selectSeat(row, 'H')" :class="getSeatClass(row, 'H', true)">H</button>
            <div class="h-10"></div> <button @click="selectSeat(row, 'K')" :class="getSeatClass(row, 'K', true)">K</button>
          </div>
        </div>

        <div class="px-12">
          <div v-for="row in economyRows" :key="row" class="grid grid-cols-7 gap-3 mb-2 items-center">
            <div class="text-[10px] font-bold text-slate-300 text-center">{{ row }}</div>
            
            <button v-for="col in ['A', 'B', 'C']" :key="col" 
              @click="selectSeat(row, col)" 
              :class="getSeatClass(row, col)">
              <span v-if="isBassinet(row, col)" class="text-[8px]">🍼</span>
              <span v-else>{{ col }}</span>
            </button>

            <div class="flex items-center justify-center">
               <div v-if="row === 41 || row === 74" class="h-8 w-full bg-red-50 rounded flex items-center justify-center animate-pulse">
                 <span class="text-[8px] font-black text-red-500 rotate-90">EXIT</span>
               </div>
            </div>

            <button v-for="col in ['H', 'J', 'K']" :key="col" 
              @click="selectSeat(row, col)" 
              :class="getSeatClass(row, col)">
              {{ col }}
            </button>
          </div>
        </div>

        <div class="my-10 flex justify-center gap-10 border-y-2 border-slate-50 py-6">
           <div class="flex flex-col items-center gap-2">
             <div class="w-20 h-14 bg-slate-800 rounded-xl flex items-center justify-center text-white text-xl">🚻</div>
             <span class="text-[8px] font-bold text-slate-400">MID LAVATORY</span>
           </div>
           <div class="flex flex-col items-center gap-2">
             <div class="w-20 h-14 bg-blue-50 rounded-xl flex items-center justify-center border-2 border-blue-100">
               <span class="text-[10px] font-bold text-blue-800">GALLEY</span>
             </div>
             <span class="text-[8px] font-bold text-slate-400">MID SERVICE</span>
           </div>
        </div>

      </div>

      <div class="mt-16 p-6 bg-slate-50 rounded-2xl grid grid-cols-3 md:grid-cols-5 gap-4">
        <div class="flex items-center gap-2 text-[10px] font-bold text-slate-600">
          <div class="w-4 h-4 bg-blue-800 rounded"></div> Business
        </div>
        <div class="flex items-center gap-2 text-[10px] font-bold text-slate-600">
          <div class="w-4 h-4 bg-orange-400 rounded"></div> Wheelchair
        </div>
        <div class="flex items-center gap-2 text-[10px] font-bold text-slate-600">
          <div class="w-4 h-4 bg-lime-400 rounded"></div> Nut Allergy
        </div>
        <div class="flex items-center gap-2 text-[10px] font-bold text-slate-600">
          <div class="w-4 h-4 bg-red-500 rounded"></div> Exit Row
        </div>
        <div class="flex items-center gap-2 text-[10px] font-bold text-slate-600">
          <div class="w-4 h-4 bg-sky-400 rounded"></div> Minor
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const selectedSeat = ref(null);

// Specific Rows for A321neo LR
const economyRows = [
  31, 32, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 
  61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74
];

const isBassinet = (row, col) => row === 31 && (col === 'A' || col === 'K');
const isMinor = (row, col) => row === 32 && col === 'B';
const isNutAllergy = (row, col) => row === 3 && col === 'K';

const selectSeat = (row, col) => {
  selectedSeat.value = `${row}${col}`;
};

const getSeatClass = (row, col, isBusiness = false) => {
  const base = "h-10 w-full rounded-lg text-[11px] font-black transition-all flex items-center justify-center border-b-4 ";
  const seatId = `${row}${col}`;

  if (selectedSeat.value === seatId) return base + "bg-blue-600 border-blue-800 text-white scale-110 shadow-lg";
  if (isBusiness) return base + "bg-blue-900 border-blue-950 text-white hover:bg-blue-800";
  if (row === 41 || row === 74) return base + "bg-red-100 border-red-300 text-red-700 hover:bg-red-200";
  if (isBassinet(row, col)) return base + "bg-sky-50 border-sky-200 text-sky-700";
  if (isNutAllergy(row, col)) return base + "bg-lime-400 border-lime-600 text-lime-900";
  
  return base + "bg-slate-200 border-slate-300 text-slate-500 hover:bg-slate-300";
};
</script>