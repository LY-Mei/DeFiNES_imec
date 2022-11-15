workload = {
    -1: {'equation': 'input',
         'loop_dim_size': {'B': 1, 'K': 3, 'OY': 64, 'OX': 64},
         'precision': 8,
         'core_allocation': 1,
         'memory_operand_links': {'O': 'I1'}
    },
    0: {  # conv1, stride 2
        'equation': 'O[b][k][oy][ox]+=W[k][c][fy][fx]*I[b][c][ix][iy]',
        'equation_relations': ['ix=2*ox+1*fx', 'iy=2*oy+1*fy'],
        'loop_dim_size': {'B': 1, 'K': 16, 'C': 3, 'OY': 64, 'OX': 64, 'FY': 7, 'FX': 7},
        'operand_precision': {'O': 16, 'O_final': 8, 'W': 8, 'I': 8},
        'operand_source': {'W': [], 'I': [-1]},
        'operand_source_dimension_mapping': {'I': {'IX': 'OX', 'IY': 'OY', 'C': 'K'}},
        'constant_operands': ['W'],
        'core_allocation': 1,
        'spatial_mapping': {'D1': ('K', 16), 'D2': ('C', 3)},
        'memory_operand_links': {'O': 'O', 'W': 'I2', 'I': 'I1'}
    }
}
