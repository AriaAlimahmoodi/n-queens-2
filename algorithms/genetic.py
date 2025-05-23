import torch
import random

class GeneticFastGPU:
    def __init__(self, n, pop_size=300, generations=5000, mutation_rate=0.2, elite_ratio=0.05, stagnation_limit=100):
        self.n = n
        self.pop_size = pop_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = int(pop_size * elite_ratio)
        self.stagnation_limit = stagnation_limit
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def solve(self):
        population = torch.stack([torch.randperm(self.n) for _ in range(self.pop_size)]).to(self.device)
        best_attacks = float('inf')
        stagnation = 0

        for gen in range(self.generations):
            fitness_scores = -self.count_attacks_batch(population)
            best_idx = torch.argmax(fitness_scores)
            best_chromo = population[best_idx].clone().cpu().numpy()
            best_chromo_attacks = -fitness_scores[best_idx].item()

            if best_chromo_attacks == 0:
                return best_chromo.tolist()

            if best_chromo_attacks < best_attacks:
                best_attacks = best_chromo_attacks
                stagnation = 0
            else:
                stagnation += 1
                if stagnation >= self.stagnation_limit:
                    return None

            elite = population[fitness_scores.argsort(descending=True)[:self.elite_size]]
            selected = self.selection(population, fitness_scores)

            next_gen = [elite[i] for i in range(self.elite_size)]
            while len(next_gen) < self.pop_size:
                p1, p2 = random.sample(selected, 2)
                child = self.crossover(p1, p2)
                if random.random() < self.mutation_rate:
                    self.mutate(child)
                next_gen.append(child)

            population = torch.stack(next_gen).to(self.device)

        return None

    def count_attacks_batch(self, batch):
        n = batch.size(1)
        attacks = torch.zeros(batch.size(0), device=self.device)

        for i in range(n):
            for j in range(i + 1, n):
                same_diag = (batch[:, i] - batch[:, j]).abs() == (i - j)
                attacks += same_diag.float()

        return attacks

    def selection(self, population, fitness_scores):
        probs = (fitness_scores - fitness_scores.min()) + 1e-6
        probs = probs / probs.sum()
        indices = torch.multinomial(probs, self.pop_size - self.elite_size, replacement=True)
        return [population[i] for i in indices]

    def crossover(self, parent1, parent2):
        start, end = sorted(random.sample(range(self.n), 2))
        child = [-1] * self.n
        child[start:end] = parent1[start:end].tolist()
        fill_values = [x.item() for x in parent2 if x.item() not in child]
        ptr = 0
        for i in range(self.n):
            if child[i] == -1:
                child[i] = fill_values[ptr]
                ptr += 1
        return torch.tensor(child, device=self.device)

    def mutate(self, chromo):
        i, j = random.sample(range(self.n), 2)
        chromo[i], chromo[j] = chromo[j], chromo[i]
