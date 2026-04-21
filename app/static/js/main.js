import * as THREE from 'https://unpkg.com/three@0.128.0/build/three.module.js';

console.log('Three.js загружен, инициализация космического фона...');

// Сцена
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0F172A); // Явный тёмно-синий фон
scene.fog = new THREE.FogExp2(0x0F172A, 0.008);

// Камера
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 2, 15);
camera.lookAt(0, 0, 0);

// Рендерер
const renderer = new THREE.WebGLRenderer({ alpha: false }); // alpha: false для непрозрачного фона
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x0F172A, 1); // Явный цвет фона
renderer.setPixelRatio(window.devicePixelRatio);

// Добавляем канвас в секцию hero
const heroSection = document.querySelector('.hero');
if (heroSection) {
    renderer.domElement.style.position = 'absolute';
    renderer.domElement.style.top = '0';
    renderer.domElement.style.left = '0';
    renderer.domElement.style.width = '100%';
    renderer.domElement.style.height = '100%';
    renderer.domElement.style.zIndex = '1';
    renderer.domElement.style.pointerEvents = 'none';
    heroSection.style.position = 'relative';
    heroSection.style.minHeight = '100vh';
    heroSection.insertBefore(renderer.domElement, heroSection.firstChild);
    console.log('Канвас добавлен в .hero');
} else {
    console.error('Секция .hero не найдена!');
}

// ========== ПУЛ ЦВЕТОВ ==========
const colorPalette = [
    { main: 0x44aaff, emissive: 0x003355, rim: 0x88ccff },
    { main: 0xaa44ff, emissive: 0x220044, rim: 0xcc88ff },
    { main: 0xff44aa, emissive: 0x440022, rim: 0xff88cc },
    { main: 0x44ff88, emissive: 0x004422, rim: 0x88ffbb },
    { main: 0x66ffcc, emissive: 0x004433, rim: 0xaaffdd },
    { main: 0xdd44ff, emissive: 0x330044, rim: 0xee88ff },
    { main: 0x44ffdd, emissive: 0x004433, rim: 0x88ffdd },
    { main: 0xdd88ff, emissive: 0x331144, rim: 0xeeaaff },
    { main: 0xff6688, emissive: 0x441122, rim: 0xffaacc },
    { main: 0x88ff44, emissive: 0x224400, rim: 0xaaff88 },
    { main: 0x88aaff, emissive: 0x112244, rim: 0xaaccff },
    { main: 0x77ddff, emissive: 0x003344, rim: 0xaaeeff },
    { main: 0xbb77ff, emissive: 0x220044, rim: 0xddaaff },
    { main: 0xff77aa, emissive: 0x441122, rim: 0xffbbcc },
    { main: 0x55ffaa, emissive: 0x004422, rim: 0xaaffcc },
    { main: 0x99ccff, emissive: 0x002244, rim: 0xcceeff },
    { main: 0xcc99ff, emissive: 0x221144, rim: 0xeebbff },
    { main: 0x66ccff, emissive: 0x003355, rim: 0xaaddff },
    { main: 0xff66cc, emissive: 0x441133, rim: 0xffaaee },
    { main: 0x33ff99, emissive: 0x004422, rim: 0x99ffcc }
];

const crystalSizes = [
    0.4, 0.4, 0.4, 0.4, 0.4,
    0.6, 0.6, 0.6, 0.6, 0.6,
    0.8, 0.8, 0.8,
    1.1, 1.3
];

function createCrystal(size) {
    const randomColor = colorPalette[Math.floor(Math.random() * colorPalette.length)];
    const geometry = new THREE.IcosahedronGeometry(size, 0);
    const material = new THREE.MeshStandardMaterial({
        color: randomColor.main,
        emissive: randomColor.emissive,
        emissiveIntensity: 0.4,
        shininess: 85,
        transparent: true,
        opacity: 0.92,
        metalness: 0.7,
        roughness: 0.3
    });
    const crystal = new THREE.Mesh(geometry, material);
    const edgesGeo = new THREE.EdgesGeometry(geometry);
    const edgesMat = new THREE.LineBasicMaterial({ color: randomColor.rim });
    const wireframe = new THREE.LineSegments(edgesGeo, edgesMat);
    crystal.add(wireframe);
    const innerGeo = new THREE.IcosahedronGeometry(size * 0.55, 0);
    const innerMat = new THREE.MeshStandardMaterial({
        color: randomColor.rim,
        emissive: randomColor.emissive,
        emissiveIntensity: 0.3,
        shininess: 100,
        transparent: true,
        opacity: 0.6
    });
    const innerCrystal = new THREE.Mesh(innerGeo, innerMat);
    crystal.add(innerCrystal);
    return crystal;
}

function getRandomPosition() {
    return {
        x: (Math.random() - 0.5) * 16,
        y: (Math.random() - 0.5) * 12,
        z: (Math.random() - 0.5) * 10 - 5
    };
}

const crystals = [];
const crystalStartPositions = [];

console.log('Создаём кристаллы...');
for (let i = 0; i < crystalSizes.length; i++) {
    const randomPos = getRandomPosition();
    const crystal = createCrystal(crystalSizes[i]);
    crystal.position.set(randomPos.x, randomPos.y, randomPos.z);
    crystal.userData = {
        rotSpeedX: (Math.random() - 0.5) * 0.02,
        rotSpeedY: (Math.random() - 0.5) * 0.02,
        rotSpeedZ: (Math.random() - 0.5) * 0.015,
        isMoving: false,
        targetPos: { x: randomPos.x, y: randomPos.y, z: randomPos.z },
        startPos: { x: randomPos.x, y: randomPos.y, z: randomPos.z },
        moveProgress: 0,
        idleOffsetX: Math.random() * Math.PI * 2,
        idleOffsetY: Math.random() * Math.PI * 2
    };
    scene.add(crystal);
    crystals.push(crystal);
    crystalStartPositions.push({ ...randomPos });
}
console.log(`Создано ${crystals.length} кристаллов`);

// Частицы (звёзды) - увеличенные и яркие
const particleCount = 3000;
const particleGeo = new THREE.BufferGeometry();
const particlePositions = new Float32Array(particleCount * 3);
const particleColors = new Float32Array(particleCount * 3);

for (let i = 0; i < particleCount; i++) {
    particlePositions[i * 3] = (Math.random() - 0.5) * 40;
    particlePositions[i * 3 + 1] = (Math.random() - 0.5) * 25;
    particlePositions[i * 3 + 2] = (Math.random() - 0.5) * 30 - 15;
    const colorChoice = Math.random();
    if (colorChoice < 0.33) {
        particleColors[i * 3] = 0.3;
        particleColors[i * 3 + 1] = 0.7;
        particleColors[i * 3 + 2] = 1.0;
    } else if (colorChoice < 0.66) {
        particleColors[i * 3] = 0.8;
        particleColors[i * 3 + 1] = 0.4;
        particleColors[i * 3 + 2] = 1.0;
    } else {
        particleColors[i * 3] = 0.4;
        particleColors[i * 3 + 1] = 0.9;
        particleColors[i * 3 + 2] = 0.6;
    }
}

particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
particleGeo.setAttribute('color', new THREE.BufferAttribute(particleColors, 3));
const particleMat = new THREE.PointsMaterial({ size: 0.08, vertexColors: true, transparent: true, opacity: 0.7, blending: THREE.AdditiveBlending });
const particles = new THREE.Points(particleGeo, particleMat);
scene.add(particles);

// Пыль (мелкие точки)
const dustCount = 5000;
const dustGeo = new THREE.BufferGeometry();
const dustPositions = new Float32Array(dustCount * 3);
for (let i = 0; i < dustCount; i++) {
    dustPositions[i * 3] = (Math.random() - 0.5) * 45;
    dustPositions[i * 3 + 1] = (Math.random() - 0.5) * 30;
    dustPositions[i * 3 + 2] = (Math.random() - 0.5) * 35 - 18;
}
dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPositions, 3));
const dustMat = new THREE.PointsMaterial({ color: 0xaaddff, size: 0.03, transparent: true, opacity: 0.25, blending: THREE.AdditiveBlending });
const dust = new THREE.Points(dustGeo, dustMat);
scene.add(dust);

// ========== ОСВЕЩЕНИЕ (усиленное) ==========
const ambientLight = new THREE.AmbientLight(0x334455, 0.6);
scene.add(ambientLight);

const mainLight = new THREE.DirectionalLight(0xffcc88, 1.2);
mainLight.position.set(3, 5, 4);
mainLight.castShadow = false;
scene.add(mainLight);

const backLight = new THREE.DirectionalLight(0x8866ff, 0.8);
backLight.position.set(-3, -1, -5);
scene.add(backLight);

const fillLight = new THREE.PointLight(0xff6600, 0.6);
fillLight.position.set(1, -1, 2);
scene.add(fillLight);

const rimLight = new THREE.PointLight(0xffaa88, 0.5);
rimLight.position.set(-2, 1, -3);
scene.add(rimLight);

const colorLights = [];
const lightColors = [0xff4422, 0x44aaff, 0xaa44ff];
for (let i = 0; i < 3; i++) {
    const light = new THREE.PointLight(lightColors[i], 0.4);
    scene.add(light);
    colorLights.push(light);
}

// Добавляем вспомогательный свет снизу
const bottomLight = new THREE.PointLight(0x44aaff, 0.3);
bottomLight.position.set(0, -4, 0);
scene.add(bottomLight);

let time = 0;
let movingCrystalIndex = -1;

function startRandomMove() {
    if (movingCrystalIndex !== -1) return;
    const idx = Math.floor(Math.random() * crystals.length);
    const crystal = crystals[idx];
    if (crystal.userData.isMoving) return;
    const newTarget = getRandomPosition();
    crystal.userData.isMoving = true;
    crystal.userData.targetPos = newTarget;
    crystal.userData.startPos = { x: crystal.position.x, y: crystal.position.y, z: crystal.position.z };
    crystal.userData.moveProgress = 0;
    movingCrystalIndex = idx;
}

setTimeout(() => startRandomMove(), 3000);
setInterval(() => { if (movingCrystalIndex === -1) startRandomMove(); }, 8000);

function animate() {
    requestAnimationFrame(animate);
    time += 0.016;
    
    crystals.forEach((crystal, idx) => {
        crystal.rotation.x += crystal.userData.rotSpeedX;
        crystal.rotation.y += crystal.userData.rotSpeedY;
        crystal.rotation.z += crystal.userData.rotSpeedZ;
        
        if (!crystal.userData.isMoving) {
            const offsetX = Math.sin(time * 0.5 + crystal.userData.idleOffsetX) * 0.08;
            const offsetY = Math.cos(time * 0.4 + crystal.userData.idleOffsetY) * 0.08;
            crystal.position.x = crystalStartPositions[idx].x + offsetX;
            crystal.position.y = crystalStartPositions[idx].y + offsetY;
        } else {
            const progress = crystal.userData.moveProgress;
            if (progress < 1) {
                const newProgress = Math.min(progress + 0.005, 1);
                const easeProgress = newProgress < 0.5 ? 2 * newProgress * newProgress : 1 - Math.pow(-2 * newProgress + 2, 2) / 2;
                crystal.position.x = crystal.userData.startPos.x + (crystal.userData.targetPos.x - crystal.userData.startPos.x) * easeProgress;
                crystal.position.y = crystal.userData.startPos.y + (crystal.userData.targetPos.y - crystal.userData.startPos.y) * easeProgress;
                crystal.position.z = crystal.userData.startPos.z + (crystal.userData.targetPos.z - crystal.userData.startPos.z) * easeProgress;
                crystal.userData.moveProgress = newProgress;
            } else {
                crystal.userData.isMoving = false;
                crystal.userData.moveProgress = 0;
                crystalStartPositions[idx] = { x: crystal.position.x, y: crystal.position.y, z: crystal.position.z };
                movingCrystalIndex = -1;
            }
        }
    });
    
    particles.rotation.y += 0.0005;
    particles.rotation.x = Math.sin(time * 0.1) * 0.05;
    dust.rotation.y -= 0.0004;
    dust.rotation.x += 0.0003;
    
    const intensity = 0.4 + Math.sin(time * 1.8) * 0.2;
    fillLight.intensity = intensity;
    rimLight.intensity = 0.4 + Math.sin(time * 1.5) * 0.15;
    bottomLight.intensity = 0.25 + Math.sin(time * 1.2) * 0.1;
    
    colorLights.forEach((light, i) => {
        const angle = time * 0.5 + i * Math.PI * 2 / 3;
        light.position.x = Math.sin(angle) * 5;
        light.position.z = Math.cos(angle) * 4 - 3;
        light.intensity = 0.35 + Math.sin(time * 1.3 + i) * 0.2;
    });
    
    renderer.render(scene, camera);
}

animate();
console.log('Анимация запущена, кристаллы должны быть видны');

window.addEventListener('resize', onWindowResize, false);
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// Эффекты для скролла хедера
window.addEventListener('scroll', function() {
    const header = document.getElementById('mainHeader');
    if (header) {
        if (window.scrollY > 50) header.classList.add('scrolled');
        else header.classList.remove('scrolled');
    }
});

// Логика слайдера
(function() {
    const images = document.querySelectorAll('.slider-image');
    const dots = document.querySelectorAll('.dot');
    const prevBtn = document.querySelector('.slider-prev');
    const nextBtn = document.querySelector('.slider-next');
    let currentIndex = 0;
    
    if (images.length === 0) return;
    
    function showImage(index) {
        if (index < 0) index = 0;
        if (index >= images.length) index = images.length - 1;
        
        images.forEach(img => img.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        
        images[index].classList.add('active');
        if (dots[index]) dots[index].classList.add('active');
        currentIndex = index;
    }
    
    function nextImage() {
        let newIndex = currentIndex + 1;
        if (newIndex >= images.length) newIndex = 0;
        showImage(newIndex);
    }
    
    function prevImage() {
        let newIndex = currentIndex - 1;
        if (newIndex < 0) newIndex = images.length - 1;
        showImage(newIndex);
    }
    
    if (prevBtn) prevBtn.addEventListener('click', prevImage);
    if (nextBtn) nextBtn.addEventListener('click', nextImage);
    
    dots.forEach((dot, idx) => {
        dot.addEventListener('click', () => showImage(idx));
    });
    
    let autoInterval = setInterval(nextImage, 5000);
    
    const sliderLeft = document.querySelector('.slider-left');
    if (sliderLeft) {
        sliderLeft.addEventListener('mouseenter', () => clearInterval(autoInterval));
        sliderLeft.addEventListener('mouseleave', () => {
            autoInterval = setInterval(nextImage, 5000);
        });
    }
})();