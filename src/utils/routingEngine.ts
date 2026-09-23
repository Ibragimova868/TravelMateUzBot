/**
 * Real-time Routing Engine for Uzbekistan & Global Coordinates
 * Computes road-based distance and travel duration via OpenStreetMap / OSRM
 * with offline Haversine and road curvature fallback.
 */

export interface LocationResult {
  success: boolean;
  lat: number;
  lon: number;
  displayName: string;
  isCoordinate: boolean;
  errorKey?: string;
  errorMessage?: string;
}

export interface RouteResult {
  success: boolean;
  originName: string;
  destName: string;
  transportLabel: string;
  distanceMeters: number;
  durationSeconds: number;
  formattedDistance: string;
  formattedDuration: string;
  error?: string;
}

// Uzbekistan major cities, regional centers, and landmarks
export const UZ_CITIES_COORDINATES: Record<
  string,
  { lat: number; lon: number; uz: string; ru: string; en: string }
> = {
  // 12 Regions & Centers
  toshkent: { lat: 41.2995, lon: 69.2401, uz: "Toshkent shahri", ru: "г. Ташкент", en: "Tashkent" },
  tashkent: { lat: 41.2995, lon: 69.2401, uz: "Toshkent shahri", ru: "г. Ташкент", en: "Tashkent" },
  samarqand: { lat: 39.6542, lon: 66.9597, uz: "Samarqand", ru: "Самарканд", en: "Samarkand" },
  samarkand: { lat: 39.6542, lon: 66.9597, uz: "Samarqand", ru: "Самарканд", en: "Samarkand" },
  buxoro: { lat: 39.7747, lon: 64.4286, uz: "Buxoro", ru: "Бухара", en: "Bukhara" },
  bukhara: { lat: 39.7747, lon: 64.4286, uz: "Buxoro", ru: "Бухара", en: "Bukhara" },
  andijon: { lat: 40.7821, lon: 72.3442, uz: "Andijon", ru: "Андижан", en: "Andijan" },
  andijan: { lat: 40.7821, lon: 72.3442, uz: "Andijon", ru: "Андижан", en: "Andijan" },
  namangan: { lat: 40.9983, lon: 71.6726, uz: "Namangan", ru: "Наманган", en: "Namangan" },
  fargona: { lat: 40.3842, lon: 71.7843, uz: "Farg‘ona", ru: "Фергана", en: "Fergana" },
  fergana: { lat: 40.3842, lon: 71.7843, uz: "Farg‘ona", ru: "Фергана", en: "Fergana" },
  qarshi: { lat: 38.8606, lon: 65.7891, uz: "Qarshi", ru: "Карши", en: "Karshi" },
  karshi: { lat: 38.8606, lon: 65.7891, uz: "Qarshi", ru: "Карши", en: "Karshi" },
  termiz: { lat: 37.2242, lon: 67.2783, uz: "Termiz", ru: "Термез", en: "Termez" },
  termez: { lat: 37.2242, lon: 67.2783, uz: "Termiz", ru: "Термез", en: "Termez" },
  nukus: { lat: 42.4619, lon: 59.6166, uz: "Nukus", ru: "Нукус", en: "Nukus" },
  urganch: { lat: 41.5562, lon: 60.6317, uz: "Urganch", ru: "Ургенч", en: "Urgench" },
  urgench: { lat: 41.5562, lon: 60.6317, uz: "Urganch", ru: "Ургенч", en: "Urgench" },
  xiva: { lat: 41.3783, lon: 60.3639, uz: "Xiva", ru: "Хива", en: "Khiva" },
  khiva: { lat: 41.3783, lon: 60.3639, uz: "Xiva", ru: "Хива", en: "Khiva" },
  navoiy: { lat: 40.0844, lon: 65.3792, uz: "Navoiy", ru: "Навои", en: "Navoi" },
  navoi: { lat: 40.0844, lon: 65.3792, uz: "Navoiy", ru: "Навои", en: "Navoi" },
  jizzax: { lat: 40.1158, lon: 67.8422, uz: "Jizzax", ru: "Джизак", en: "Jizzakh" },
  jizzakh: { lat: 40.1158, lon: 67.8422, uz: "Jizzax", ru: "Джизак", en: "Jizzakh" },
  guliston: { lat: 40.4897, lon: 68.7842, uz: "Guliston", ru: "Гулистан", en: "Gulistan" },
  gulistan: { lat: 40.4897, lon: 68.7842, uz: "Guliston", ru: "Гулистан", en: "Gulistan" },
  sirdaryo: { lat: 40.8436, lon: 68.6617, uz: "Sirdaryo", ru: "Сырдарья", en: "Sirdaryo" },
  surxondaryo: { lat: 37.9409, lon: 67.5708, uz: "Surxondaryo", ru: "Сурхандарья", en: "Surkhandarya" },
  qashqadaryo: { lat: 38.8986, lon: 65.7925, uz: "Qashqadaryo", ru: "Кашкадарья", en: "Kashkadarya" },
  xorazm: { lat: 41.5345, lon: 60.6249, uz: "Xorazm", ru: "Хорезм", en: "Khorezm" },

  // Key Cities, Tourist & Industrial Hubs
  qoqon: { lat: 40.5286, lon: 70.9425, uz: "Qo‘qon", ru: "Коканд", en: "Kokand" },
  kokand: { lat: 40.5286, lon: 70.9425, uz: "Qo‘qon", ru: "Коканд", en: "Kokand" },
  margilon: { lat: 40.4725, lon: 71.7161, uz: "Marg‘ilon", ru: "Маргилан", en: "Margilan" },
  margilan: { lat: 40.4725, lon: 71.7161, uz: "Marg‘ilon", ru: "Маргилан", en: "Margilan" },
  shahrisabz: { lat: 39.0558, lon: 66.8306, uz: "Shahrisabz", ru: "Шахрисабз", en: "Shakhrisabz" },
  shakhrisabz: { lat: 39.0558, lon: 66.8306, uz: "Shahrisabz", ru: "Шахрисабз", en: "Shakhrisabz" },
  chirchiq: { lat: 41.4689, lon: 69.5822, uz: "Chirchiq", ru: "Чирчик", en: "Chirchiq" },
  angren: { lat: 41.0167, lon: 70.1436, uz: "Angren", ru: "Ангрен", en: "Angren" },
  olmaliq: { lat: 40.8500, lon: 69.6000, uz: "Olmaliq", ru: "Алмалык", en: "Almalyk" },
  bekobod: { lat: 40.2167, lon: 69.2167, uz: "Bekobod", ru: "Бекабад", en: "Bekabad" },
  zarafshon: { lat: 41.5722, lon: 64.1958, uz: "Zarafshon", ru: "Зарафшан", en: "Zarafshan" },
  denov: { lat: 38.2667, lon: 67.9000, uz: "Denov", ru: "Денау", en: "Denau" },
  asaka: { lat: 40.6414, lon: 72.2389, uz: "Asaka", ru: "Асака", en: "Asaka" },
  chust: { lat: 41.0000, lon: 71.2333, uz: "Chust", ru: "Чуст", en: "Chust" },
  chimboy: { lat: 42.9406, lon: 59.7753, uz: "Chimboy", ru: "Чимбай", en: "Chimboy" },
  shovot: { lat: 41.6500, lon: 60.3000, uz: "Shovot", ru: "Шават", en: "Shavat" },
  xonobod: { lat: 40.8033, lon: 73.0033, uz: "Xonobod", ru: "Ханабад", en: "Khanabad" },
  zomin: { lat: 39.9606, lon: 68.4950, uz: "Zomin", ru: "Заамин", en: "Zaamin" },
  chimgan: { lat: 41.5167, lon: 70.0000, uz: "Chimyon (Chimgan)", ru: "Чимган", en: "Chimgan" },
  chorvoq: { lat: 41.6289, lon: 70.0461, uz: "Chorvoq", ru: "Чарвак", en: "Charvak" }
};

/**
 * Normalizes input text for city search
 */
function normalizeKey(str: string): string {
  return str
    .toLowerCase()
    .replace(/[‘'’`"«»]/g, "")
    .replace(/\s+/g, "")
    .trim();
}

/**
 * Checks if input is in coordinates format: "LAT, LON"
 */
export function parseCoordinates(
  input: string
): { isCoord: boolean; lat?: number; lon?: number; valid?: boolean } {
  const clean = input.trim();
  if (!clean.includes(",")) {
    return { isCoord: false };
  }

  const parts = clean.split(",");
  if (parts.length !== 2) {
    return { isCoord: false };
  }

  const lat = parseFloat(parts[0].trim());
  const lon = parseFloat(parts[1].trim());

  if (isNaN(lat) || isNaN(lon)) {
    return { isCoord: false };
  }

  // Validate range
  const valid = lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
  return { isCoord: true, lat, lon, valid };
}

/**
 * Calculates Haversine distance in meters between two lat/lon coordinates
 */
export function calculateHaversineDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371000; // Earth radius in meters
  const toRad = (deg: number) => (deg * Math.PI) / 180;

  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) *
      Math.cos(toRad(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Resolves location input (Coordinates or Address/City)
 */
export async function resolveLocation(
  query: string,
  lang: "uz" | "ru" | "en" = "uz"
): Promise<LocationResult> {
  const clean = query.trim();

  // 1. Check coordinates
  const coord = parseCoordinates(clean);
  if (coord.isCoord) {
    if (!coord.valid || coord.lat === undefined || coord.lon === undefined) {
      return {
        success: false,
        lat: 0,
        lon: 0,
        displayName: clean,
        isCoordinate: true,
        errorKey: "invalid_coordinates",
        errorMessage:
          lang === "uz"
            ? "Noto‘g‘ri koordinata kiritildi. Iltimos, quyidagi formatda kiriting:\n39.7747, 64.4286\n(Kenglik: -90 dan 90 gacha, Uzunlik: -180 dan 180 gacha)"
            : lang === "ru"
            ? "Неверные координаты. Пожалуйста, используйте следующий формат:\n39.7747, 64.4286\n(Широта: от -90 до 90, Долгота: от -180 до 180)"
            : "Invalid coordinates. Please use this format:\n39.7747, 64.4286\n(Latitude: -90 to 90, Longitude: -180 to 180)"
      };
    }

    return {
      success: true,
      lat: coord.lat,
      lon: coord.lon,
      displayName: `${coord.lat.toFixed(4)}, ${coord.lon.toFixed(4)}`,
      isCoordinate: true
    };
  }

  // 2. Check local database
  const normalized = normalizeKey(clean);
  for (const [key, val] of Object.entries(UZ_CITIES_COORDINATES)) {
    if (normalized === key || normalized.includes(key) || key.includes(normalized)) {
      return {
        success: true,
        lat: val.lat,
        lon: val.lon,
        displayName: `${val[lang]}, O‘zbekiston`,
        isCoordinate: false
      };
    }
  }

  // 3. Query OpenStreetMap Nominatim with timeout
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3500);

    const nominatimUrl = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(
      clean + ", Uzbekistan"
    )}&format=json&limit=1`;

    const res = await fetch(nominatimUrl, {
      headers: { "Accept-Language": lang },
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        const item = data[0];
        return {
          success: true,
          lat: parseFloat(item.lat),
          lon: parseFloat(item.lon),
          displayName: item.display_name.split(",").slice(0, 3).join(","),
          isCoordinate: false
        };
      }
    }
  } catch (err) {
    // Network or abort error, continue to fallback
  }

  // Fallback: If not found, return address error
  return {
    success: false,
    lat: 0,
    lon: 0,
    displayName: clean,
    isCoordinate: false,
    errorKey: "route_address_not_found",
    errorMessage:
      lang === "uz"
        ? `Kechirasiz, '${clean}' manzili topilmadi. Iltimos, manzil nomini to‘g‘riroq yoki kengroq qilib yozing.`
        : lang === "ru"
        ? `Извините, адрес '${clean}' не найден. Пожалуйста, проверьте написание.`
        : `Sorry, address '${clean}' could not be found. Please check spelling.`
  };
}

/**
 * Format distance strictly according to requirements
 */
export function formatDistance(meters: number, lang: "uz" | "ru" | "en"): string {
  if (meters >= 1000) {
    const km = meters / 1000;
    const rounded = km >= 10 ? Math.round(km) : Math.round(km * 10) / 10;
    if (lang === "ru") return `${rounded} км`;
    return `${rounded} km`;
  }
  const m = Math.round(meters);
  if (lang === "ru") return `${m} м`;
  return `${m} m`;
}

/**
 * Format duration strictly according to requirements
 */
export function formatDuration(seconds: number, lang: "uz" | "ru" | "en"): string {
  const totalMinutes = Math.max(1, Math.round(seconds / 60));
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;

  if (hours > 0) {
    if (lang === "uz") {
      return minutes > 0 ? `${hours} soat ${minutes} daqiqa` : `${hours} soat`;
    } else if (lang === "ru") {
      return minutes > 0 ? `${hours} ч ${minutes} мин` : `${hours} ч`;
    } else {
      return minutes > 0 ? `${hours} h ${minutes} min` : `${hours} h`;
    }
  }

  if (lang === "uz") return `${minutes} daqiqa`;
  if (lang === "ru") return `${minutes} мин`;
  return `${minutes} min`;
}

/**
 * Calculates road route distance and duration for given transport mode
 */
export async function calculateRouteDistance(
  startLat: number,
  startLon: number,
  endLat: number,
  endLon: number,
  transportKey: "car" | "moto" | "bike" | "walk",
  lang: "uz" | "ru" | "en"
): Promise<{ distanceMeters: number; durationSeconds: number }> {
  // Map transport mode to OSRM profile
  const osrmProfileMap: Record<string, string> = {
    car: "car",
    moto: "car",
    bike: "bicycle",
    walk: "foot"
  };
  const profile = osrmProfileMap[transportKey] || "car";

  // Try OSRM public API
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);

    const osrmUrl = `https://router.project-osrm.org/route/v1/${profile}/${startLon},${startLat};${endLon},${endLat}?overview=false`;
    const res = await fetch(osrmUrl, { signal: controller.signal });
    clearTimeout(timeoutId);

    if (res.ok) {
      const data = await res.json();
      if (data.code === "Ok" && data.routes && data.routes.length > 0) {
        let dist = data.routes[0].distance;
        let dur = data.routes[0].duration;

        if (transportKey === "moto") {
          // Motorcycle travels slightly faster on intercity roads
          dur = Math.max(60, dur * 0.9);
        }

        return {
          distanceMeters: Math.round(dist),
          durationSeconds: Math.round(dur)
        };
      }
    }
  } catch (err) {
    // OSRM failed or offline, proceed to calibrated road calculation
  }

  // Haversine fallback with realistic road winding coefficient and vehicle speeds
  const straightDistance = calculateHaversineDistance(
    startLat,
    startLon,
    endLat,
    endLon
  );

  // Winding factors: roads are not straight lines
  const windingFactors = {
    car: 1.28,
    moto: 1.28,
    bike: 1.20,
    walk: 1.15
  };

  const winding = windingFactors[transportKey] || 1.28;
  const distanceMeters = Math.round(straightDistance * winding);

  // Realistic travel speeds (m/s)
  // Car: ~72 km/h (20 m/s) on highways, ~40 km/h in cities
  // Moto: ~68 km/h (18.9 m/s)
  // Bike: ~15 km/h (4.17 m/s)
  // Walk: ~4.5 km/h (1.25 m/s)
  const isCityTrip = distanceMeters < 15000;
  let speedMps = 20; // default car highway

  if (transportKey === "car") {
    speedMps = isCityTrip ? 11.1 : 20.0; // 40 km/h vs 72 km/h
  } else if (transportKey === "moto") {
    speedMps = isCityTrip ? 12.5 : 19.5;
  } else if (transportKey === "bike") {
    speedMps = 4.17; // 15 km/h
  } else if (transportKey === "walk") {
    speedMps = 1.25; // 4.5 km/h
  }

  const durationSeconds = Math.round(distanceMeters / speedMps);

  return {
    distanceMeters,
    durationSeconds
  };
}
