const portalConfig = {
    mundos: {
        'math': { 
            nombre: 'MATH_DEPT', // Usaremos estas claves para traducir luego
            color: '#00f341',    // Tu verde Matrix que te gusta
            clase: 'math-world' 
        },
        'geometry': { 
            nombre: 'SACRED_GEO', 
            color: '#ffcc00', 
            clase: 'geo-world' 
        },
        'audio': { 
            nombre: 'AUDIO_LABS', 
            color: '#00f3ff', 
            clase: 'audio-world' 
        }
    },
    proyectos: [
        {
            id: 'magic-square',
            folder: 'magic-square',
            mundos: ['math', 'geometry'], // Aparece en ambos mundos
            tags: ['matrix', 'order']
        },
        {
            id: 'chaos-lab',
            folder: 'chaos-lab',
            mundos: ['math'],
            tags: ['chaos', 'logic']
        }
        // Cuando traigas los de fuera, solo añades una línea aquí
    ]
};