import time
import os


def out_many(_key, _dir):
    # keys = _key.split('*')
    times = 3
    for i in range(times):
        name = _key.replace('*', str(i))
        with open(os.path.join(_dir, f'BTE.{name}'), 'w+') as f:
            f.write(name)
            f.write('\n-------------\n')
            t = time.localtime()
            f.write(
                f'{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}'
                f' {t.tm_sec}')
            f.write('\n-------------\n')


def out(_list, _dir):
    for key in _list:
        if key.find('*'):
            out_many(key, _dir)
        else:
            with open(os.path.join(_dir, f'BTE.{key}'), 'w+') as f:
                f.write(key)
                f.write('\n-------------\n')
                t = time.localtime()
                f.write(
                    f'{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}'
                    f' {t.tm_sec}')
                f.write('\n-------------\n')


if __name__ == "__main__":
    # with open('CONTROL', 'r') as f:
    #     string = f.read()
    import sys
    flist = []
    for i in sys.stdin:
        s = i.strip()
        if len(s) == 0:
            continue
        flist.append(s)
    print(flist, len(flist))

    out_descs_list = ['ReciprocalLatticeVectors', 'qpoints', 'qpoints_full',
                      'omega', 'v', 'v_full', 'w_boundary', 'w_isotopic', 'dos',
                      'pdos', 'P3', 'P3_total', 'P3_plus*', 'P3_minus*',
                      'gruneisen', 'cvVsT', 'gruneisenVsT_total',
                      'KappaTensorVsT_sg', 'KappaTensorVsT_RTA',
                      'KappaTensorVsT_CONV']
    out_td_list = ['cv', 'kappa_sg', 'gruneisen_total', 'WP3', 'WP3_plus',
                   'WP3_minus', 'w_anharmonic', 'w', 'w_final', 'kappa',
                   'kappa_tensor', 'kappa_scalar', 'kappa_nw_*',
                   'kappa_nw_*_lower', 'cumulative_kappa_*',
                   'cumulative_kappaVsOmega_tensor']

    out_dir = os.path.join(os.getcwd(), 'shengbte')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out(out_descs_list, out_dir)

    out_td_dir = os.path.join(out_dir, 'T300K')
    if not os.path.exists(out_td_dir):
        os.makedirs(out_td_dir)
    out(out_td_list, out_td_dir)
