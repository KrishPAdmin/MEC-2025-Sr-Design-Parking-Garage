const socket = io({ transports: ["websocket", "polling"] });

// Level 1: 3 spots for Best Buy + Canadian Tire, plus bikes
const L1_SPOTS = [
  "D1A", "D1E", "D1P",      // Dollarama
  "B1A", "B1E", "B1P",     // Best Buy (3)
  "S1A", "S1E", "S1P",     // Sephora
  "C1A", "C1E", "C1P",     // Canadian Tire (3)
  "BIKEL", "BIKER"        // Bike stands
];

// Level 2: 2 spots for Best Buy + Canadian Tire
const L2_SPOTS = [
  "D2F", "D2P1", "D2P2",   // Dollarama (3)
  "B2F", "B2P1",           // Best Buy (2)
  "S2F", "S2P1", "S2P2",   // Sephora (3)
  "C2F", "C2P1"            // Canadian Tire (2)
];

// Bike spots (we want them visible but NOT counted as vehicle spots on L1)
const L1_BIKE_SPOTS = ["BIKEL", "BIKER"];

// Only car spots on Level 1 (used for counts/bars)
const L1_VEHICLE_SPOTS = L1_SPOTS.filter(s => !L1_BIKE_SPOTS.includes(s));

const ALL_IDS = L1_SPOTS.map(s => `L1-${s}`).concat(L2_SPOTS.map(s => `L2-${s}`));

ALL_IDS.forEach(id => {
  const el = document.getElementById(id);
  if (el) {
    el.classList.add("free");
    el.classList.remove("occ");
  }
});

const counts = {
  L1: { total: L1_VEHICLE_SPOTS.length, free: L1_VEHICLE_SPOTS.length, occ: 0 },
  L2: { total: L2_SPOTS.length,         free: L2_SPOTS.length,         occ: 0 }
};

function recount() {
  ["L1", "L2"].forEach(level => {
    const list =
      (level === "L1"
        ? L1_VEHICLE_SPOTS   // Level 1: cars only (no bikes)
        : L2_SPOTS           // Level 2: all spots
      ).map(s => `${level}-${s}`);

    const occ = list.filter(id => document.getElementById(id)?.classList.contains("occ")).length;
    const free = list.length - occ;
    counts[level].occ = occ;
    counts[level].free = free;
  });

  document.getElementById("l1-free").textContent = counts.L1.free;
  document.getElementById("l1-occ").textContent = counts.L1.occ;
  document.getElementById("l2-free").textContent = counts.L2.free;
  document.getElementById("l2-occ").textContent = counts.L2.occ;

  document.getElementById("l1-bar").style.width =
    Math.round((counts.L1.free / counts.L1.total) * 100) + "%";
  document.getElementById("l2-bar").style.width =
    Math.round((counts.L2.free / counts.L2.total) * 100) + "%";
}

recount();

socket.on("spot_update", ({ level, spot, occupied }) => {
  const id = `${level}-${spot}`;
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.toggle("occ", occupied);
  el.classList.toggle("free", !occupied);
  recount();
});

const tooltip = document.getElementById("tooltip");

document.addEventListener("mousemove", (e) => {
  if (tooltip.style.display !== "none") {
    tooltip.style.left = (e.pageX + 12) + "px";
    tooltip.style.top = (e.pageY + 12) + "px";
  }
});

document.querySelectorAll(".spot.tip").forEach(el => {
  el.addEventListener("mouseenter", () => {
    const id = el.id;
    const type = el.dataset.type || "Regular";
    const occupied = el.classList.contains("occ") ? "Occupied" : "Free";
    tooltip.innerHTML = `<b>${id}</b><br>${type} • ${occupied}`;
    tooltip.style.display = "block";
  });
  el.addEventListener("mouseleave", () => {
    tooltip.style.display = "none";
  });
});
