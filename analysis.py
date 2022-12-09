import pandas as pd
import json
import cvxpy as cp


def mk_df():
    # read in data
    with open('recipe_dicts.json', 'r') as f:
        dicts = json.load(f)

    # load into DF
    df = pd.DataFrame(dicts)

    # reformat dish names
    def rm_suff(s):
        s = s.lower()
        suffs = [' - ', ' recipe']
        for suff in suffs:
            if suff in s:
                i = s.index(suff)
                s = s[:i]
        pre = 'how to make '
        if pre in s:
            i = s.index(pre)
            s = s[i + len(pre):]
        return s
    df.dish = df.dish.apply(rm_suff)
    df = df.set_index('dish')

    # drop columns
    drop_cols = [col for col in df.columns if 'unit' in col] + ['serving']
    df = df.drop(columns=drop_cols)  # drop unit col
    for col in df.columns:
        df[col] = df[col].astype(float)

    # drop dishes with nans
    df = df.dropna()

    # drop dishes where nutrition facts are wrong
    wrong_dishes = [
        'cajun potato salad',
    ]
    df = df.drop(index=wrong_dishes)
    return df


def optimize(nut_bounds, df, T):
    # sample df to make it faster
    df = df.sample(frac=0.2)

    # variables
    I = len(df)
    print(f'{I} dishes to choose from')
    x = cp.Variable((I, T), boolean=True)
    s = cp.Variable((I, T), nonneg=True)

    # minimize total cost of dishes
    obj_expr = 0
    for t in range(T):
        obj_expr += cp.sum(cp.multiply(s[:, t], df.cost_per_serving))
    obj = cp.Minimize(obj_expr)

    constraints = []
    constraints.append(s <= 3 * x)  # meals can't be more than 3 servings
    constraints.append(s >= 0.5 * x)  # meals can't be less than 0.5 servings
    constraints.append(cp.sum(x, axis=0) == 3)  # 3 meals per day
    constraints.append(cp.sum(x, axis=1) <= max(1, T * (2 / 7)))  # don't repeat meals too often
    # macros lower and upper limits
    for t in range(T):
        for nut in nut_bounds:
            lo, hi = nut_bounds[nut]
            lo_constraint = cp.sum(cp.multiply(s[:, t], df[nut])) >= lo
            hi_constraint = cp.sum(cp.multiply(s[:, t], df[nut])) <= hi
            constraints += [lo_constraint, hi_constraint]

    # solve
    prob = cp.Problem(obj, constraints)
    cost_opt = prob.solve(solver=cp.GUROBI, verbose=1)
    s_opt = s.value

    # stats
    df_opt = df.copy()
    opt_servings_sum_col = 'opt_servings_sum'
    df_opt[opt_servings_sum_col] = 0
    for t in range(T):
        opt_servings_col = f'opt_servings_{t}'
        df_opt[opt_servings_col] = s_opt[:, t]
        df_opt[opt_servings_sum_col] += df_opt[opt_servings_col]
    df_opt = df_opt[df_opt[opt_servings_sum_col] > 0]
    df_opt = df_opt.sort_values(opt_servings_sum_col, ascending=False)
    print(f'cost=${cost_opt:.2f}')
    return df_opt, cost_opt


if __name__ == '__main__':
    # read data into DF
    df = mk_df()

    nut_targs = {
        'calories': 2500,
        'carbohydrates': 319,
        'protein': 113,
        'fat': 92,
        'fiber': 27.5,
    }
    nut_bounds = {
        'sodium': [0, 2500],
    }
    for nut, targ in nut_targs.items():
        lb = 0.9 * targ
        ub = 1.1 * targ
        nut_bounds[nut] = [lb, ub]
    print(nut_bounds)

    D = 7
    df_opt, cost_opt = optimize(nut_bounds, df, D)
    df_opt.to_csv('opt.csv')
